import xarray as xr
import dscim
import yaml
from dscim.menu.simple_storage import Climate, EconVars
import pandas as pd
import numpy as np
from itertools import product
from pathlib import Path
import os
import re
import subprocess
from datetime import date

# EDIT this line upon each release of dscim-facts-epa
VERSION = "0.5.0"

discount_conversion_dict = {
    "1.016010255_9.149608e-05": "1.5% Ramsey",
    "1.244459066_0.00197263997": "2.0% Ramsey",
    "1.421158116_0.00461878399": "2.5% Ramsey",
}


# For configs that are generated in the FACTS docker, file structure is relative to the docker paths.
# This function serves to ensure that configs generated in the FACTS docker have their filepaths
# converted to paths that are relative to this script
def read_replace_conf(master):
    try:
        with open(master, "r") as stream:
            docker_replace = stream.read().replace(
                "/opt/dscim-facts-epa", str(Path(os.getcwd()).parent.absolute())
            )
            conf = yaml.safe_load(docker_replace)
    except FileNotFoundError:
        raise FileNotFoundError(
            "Please run directory_setup.py or place the config in your current working directory"
        )
    return conf


def makedir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def generate_meta(
    menu_item,
    conf,
    gas_conversion_dict,
    terr_us,
):
    # find machine name
    machine_name = os.getenv("HOSTNAME")
    if machine_name is None:
        try:
            machine_name = os.uname()[1]
        except AttributeError:
            machine_name = "unknown"

    # find git commit hash
    try:
        gitlabel = (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
            .decode("ascii")
            .strip()
        )
    except subprocess.CalledProcessError:
        gitlabel = "unknown"

    meta = {
        "Author": "Climate Impact Lab",
        "Date Created": date.today().strftime("%d/%m/%Y"),
        "Units": "2020 PPP-adjusted USD",
    }

    for attr_dict in [
        vars(menu_item),
        vars(vars(menu_item)["climate"]),
        vars(vars(menu_item)["econ_vars"]),
    ]:
        meta.update(
            {
                k: v
                for k, v in attr_dict.items()
                if (type(v) not in [xr.DataArray, xr.Dataset, pd.DataFrame])
                and k not in ["damage_function", "logger"]
            }
        )

    # update with git hash and machine name
    meta.update(
        dict(
            machine=machine_name,
            commit=gitlabel,
            url=f"https://github.com/ClimateImpactLab/dscim-facts-epa/commit/{gitlabel}",
        )
    )

    # convert to strs
    meta = {k: v if type(v) in [int, float] else str(v) for k, v in meta.items()}

    # exclude irrelevant attrs
    irrelevant_keys = [
        "econ_vars",
        "climate",
        "subset_dict",
        "filename_suffix",
        "ext_subset_start_year",
        "ext_subset_end_year",
        "ext_end_year",
        "ext_method",
        "clip_gmsl",
        "scenario_dimensions",
        "scc_quantiles",
        "quantreg_quantiles",
        "quantreg_weights",
        "full_uncertainty_quantiles",
        "extrap_formula",
        "fair_dims",
        "sector_path",
        "save_files",
        "save_path",
        "delta",
        "histclim",
        "ce_path",
        "gmst_path",
        "gmsl_path",
    ]
    for k in irrelevant_keys:
        if k in meta.keys():
            del meta[k]

    # adjust attrs
    meta["emission_scenarios"] = "RFF-SPv2"
    meta["damagefunc_base_period"] = meta.pop("base_period")
    meta["socioeconomics_path"] = meta.pop("path")
    meta["gases"] = meta["gases"].split("'")
    meta["gases"] = [e for e in meta["gases"] if e not in (", ", "[", "]")]
    meta["gases"] = [gas_conversion_dict[gas] for gas in meta["gases"]]

    if meta["sector"] == "CAMEL_m1_c0.20":
        meta["sector"] = "combined"
    else:
        meta["sector"] = re.split("_", meta["sector"])[0]

    if terr_us:
        meta.update(
            discounting_socioeconomics_path=f"{conf['rffdata']['socioec_output']}/rff_global_socioeconomics.nc4"
        )

    return meta


# Merge attrs
def merge_meta(attrs, meta):
    if len(attrs) == 0:
        attrs.update(meta)
    else:
        for meta_keys in attrs.keys():
            if str(meta[meta_keys]) not in str(attrs[meta_keys]):
                if type(attrs[meta_keys]) != list:
                    update = [attrs[meta_keys]]
                    update.append(meta[meta_keys])
                    attrs[meta_keys] = update
                else:
                    attrs[meta_keys].append(meta[meta_keys])
    return attrs


################################################################################


# Function for one run of SCGHGs
def epa_scghg(
    gas_conversion_dict,
    conf,
    sector="CAMEL_m1_c0.20",
    terr_us=False,
    eta=2.0,
    rho=0.0,
    pulse_year=2020,
    discount_type="euler_ramsey",
    menu_option="risk_aversion",
):

    # Manually add other config parameters that are not meant to change run to run
    conf["global_parameters"] = {
        "fair_aggregation": ["uncollapsed"],
        "subset_dict": {"ssp": []},
        "weitzman_parameter": [0.5],
        "save_files": [],
    }

    # there can be a molecular conversion bundled in with the conversion factor, so it isn't always just tonnes
    # for example with carbon vs carbon dioxide conversion
    gas_conversion_factors = {
        "coords": {
            "gas": {
                "dims": "gas",
                "data": list(conf["gas_conversions"].keys()),
                "attrs": {"units": "tonnes"},
            }
        },
        "dims": "gas",
        "data": list(conf["gas_conversions"].values()),
    }

    # This class allows us to bypass reading in the pulse conversion netcdf file
    # and instead set up pulse conversions from a user config file.
    class Climate2(Climate):
        @property
        def conversion(self):
            """Conversion factors to turn the pulse units
            into the appropriate units for an SCC calculation"""

            conversion = xr.DataArray.from_dict(gas_conversion_factors)
            return conversion

    # Read in U.S. and global socioeconomic files
    if terr_us:
        econ_terr_us = EconVars(
            path_econ=f"{conf['rffdata']['socioec_output']}/rff_USA_socioeconomics.nc4"
        )
        # List of kwargs to add to kwargs read in from the config file for direct territorial U.S. damages
        add_kwargs = {
            "econ_vars": econ_terr_us,
            "climate_vars": Climate2(**conf["rff_climate"], pulse_year=pulse_year),
            "formula": conf["sectors"][sector if not terr_us else sector[:-4]][
                "formula"
            ],
            "discounting_type": discount_type,
            "sector": sector,
            "ce_path": None,
            "save_path": None,
            "eta": eta,
            "rho": rho,
            "damage_function_path": Path(conf["paths"]["rff_damage_function_library"])
            / sector,
            "ecs_mask_path": None,
            "ecs_mask_name": None,
            "fair_dims": [],
        }

        # An extra set of kwargs is needed when running U.S. SCGHGs
        # Combine config kwargs with the add_kwargs for direct territorial U.S. damages
        kwargs_terr_us = conf["global_parameters"].copy()
        for k, v in add_kwargs.items():
            assert (
                k not in kwargs_terr_us.keys()
            ), f"{k} already set in config. Please check `global_parameters`."
            kwargs_terr_us.update({k: v})

    econ_glob = EconVars(
        path_econ=f"{conf['rffdata']['socioec_output']}/rff_global_socioeconomics.nc4"
    )

    # This class allows for a shorter naming convention for the damage function files (rounding etas and rhos in the filename)
    class RiskAversionRecipe(dscim.menu.risk_aversion.RiskAversionRecipe):
        @property
        def damage_function_coefficients(self) -> xr.Dataset:
            """
            Load damage function coefficients if the coefficients are provided by the user.
            Otherwise, compute them.
            """
            if self.damage_function_path is not None:
                return xr.open_dataset(
                    f"{self.damage_function_path}/{self.NAME}_{self.discounting_type}_eta{round(self.eta,3)}_rho{round(self.rho,3)}_dfc.nc4"
                )
            else:
                return self.damage_function["params"]
            
    # very poor design. copied this overloaded class to also work for adding_up recipe
    class Baseline(dscim.menu.baseline.Baseline):
        @property
        def damage_function_coefficients(self) -> xr.Dataset:
            """
            Load damage function coefficients if the coefficients are provided by the user.
            Otherwise, compute them.
            """
            if self.damage_function_path is not None:
                return xr.open_dataset(
                    f"{self.damage_function_path}/{self.NAME}_{self.discounting_type}_eta{round(self.eta,3)}_rho{round(self.rho,3)}_dfc.nc4"
                )
            else:
                return self.damage_function["params"]

    # List of kwargs to add to kwargs read in from the config file for global discounting and damages
    add_kwargs = {
        "econ_vars": econ_glob,
        "climate_vars": Climate2(**conf["rff_climate"], pulse_year=pulse_year),
        "formula": conf["sectors"][sector if not terr_us else sector[:-4]]["formula"],
        "discounting_type": discount_type,
        "sector": sector,
        "ce_path": None,
        "save_path": None,
        "eta": eta,
        "rho": rho,
        "damage_function_path": Path(conf["paths"]["rff_damage_function_library"])
        / [sector if not terr_us else sector[:-4]][0],
        "ecs_mask_path": None,
        "ecs_mask_name": None,
        "fair_dims": [],
    }

    # Combine config kwargs with the add_kwargs for global discounting and damages
    kwargs_global = conf["global_parameters"].copy()
    for k, v in add_kwargs.items():
        assert (
            k not in kwargs_global.keys()
        ), f"{k} already set in config. Please check `global_parameters`."
        kwargs_global.update({k: v})

    # For both territorial U.S. and global SCGHGs, endogenous Ramsey discounting based on global socioeconomics is used
    if menu_option == "risk_aversion":
        menu_item_global = RiskAversionRecipe(**kwargs_global)
    elif menu_option == "risk_neutral": #"adding_up":
        menu_item_global = Baseline(**kwargs_global)
    df = menu_item_global.uncollapsed_discount_factors

    # Compute damages for global or U.S. runs
    if terr_us:
        if menu_option == "risk_aversion":
            menu_item_terr_us = RiskAversionRecipe(**kwargs_terr_us)
        elif menu_option == "risk_neutral": #"adding_up":
            menu_item_terr_us = Baseline(**kwargs_terr_us)
        md = menu_item_terr_us.uncollapsed_marginal_damages
    else:
        md = menu_item_global.uncollapsed_marginal_damages

    # The 113.648/112.29 deflates the SCGHGs from 2019 dollars to 2020 dollars
    conv_2019to2020 = 113.648 / 112.29

    # Compute SCGHGs
    # Multiplying marginal damages by discount factors and summing across years creates the SCGHGs
    scghgs = (
        md.rename(marginal_damages="scghg") * df.rename(discount_factor="scghg")
    ).sum("year") * conv_2019to2020

    # Code to calculate epa-spec adjustment factors
    gcnp = menu_item_global.global_consumption_no_pulse.rename("gcnp")

    # Isolate population from socioeconomics
    pop = (
        xr.open_dataset(
            f"{conf['rffdata']['socioec_output']}/rff_global_socioeconomics.nc4"
        )
        .sel(region="world", drop=True)
        .pop
    )

    # Calculate global consumption no pulse per population
    a = xr.merge([pop, gcnp])
    ypv = a.gcnp / a.pop

    # Create adjustment factor using adjustment.factor = (ypc^-eta)/mean(ypc^-eta)
    c = np.power(ypv, -eta).sel(year=pulse_year, drop=True)
    adj = (c / c.mean()).rename("adjustment_factor")

    # Merge adjustments with uncollapsed scghgs
    adjustments = xr.merge([scghgs, adj.to_dataset()])

    # generate attrs
    if terr_us:
        meta = generate_meta(
            menu_item_terr_us,
            conf,
            gas_conversion_dict,
            True,
        )
    else:
        meta = generate_meta(
            menu_item_global,
            conf,
            gas_conversion_dict,
            False,
        )

    return [adjustments, gcnp * conv_2019to2020, meta]


# Function to perform multiple runs of SCGHGs and combine into one file to save out
def epa_scghgs(
    sectors,
    conf,
    conf_name,
    gas_conversion_dict,
    terr_us,
    etas_rhos,
    risk_combos=(("risk_aversion", "euler_ramsey")),
    pulse_years=(2020, 2030, 2040, 2050, 2060, 2070, 2080),
    gcnp=False,
    uncollapsed=False,
):
    attrs = {}

    # Nested for loops to run each combination of SCGHGs requested
    # Each run of the outer loop saves one set of SCGHGs
    # The inner loop combines all SCGHG runs for that file
    for j, pulse_year in product(risk_combos, pulse_years):

        discount_type = j[1]
        menu_option = j[0]
        for sector in sectors:
            # These arrays will be populated with data arrays to be combined
            all_arrays_uscghg = []
            all_arrays_gcnp = []

            if (menu_option == "risk_neutral") and ("CAMEL" not in sector):
                import warnings
                warnings.warn(f"Risk neutral SCGHGs are only available for the Combined sector. Skipping {sector}...")
                continue
            
            if re.split("_", sector)[0] == "CAMEL":
                sector_short = "combined"
            else:
                sector_short = re.split("_", sector)[0]

            for i in etas_rhos:

                eta = i[0]
                rho = i[1]

                print(
                    f"Calculating {'territorial U.S.' if terr_us else 'global'} {sector_short} scghgs {'and gcnp' if gcnp else ''} \n discount rate: {discount_conversion_dict[str(eta) + '_' + str(rho)]} \n pulse year: {pulse_year}"
                )
                df_single_scghg, df_single_gcnp, meta = epa_scghg(
                    gas_conversion_dict,
                    conf,
                    sector=sector,
                    terr_us=terr_us,
                    discount_type=discount_type,
                    menu_option=menu_option,
                    eta=eta,
                    rho=rho,
                    pulse_year=pulse_year,
                )

                # Creates new coordinates to differentiate between runs
                # For SCGHGs
                df_scghg = df_single_scghg.assign_coords(
                    discount_rate=discount_conversion_dict[str(eta) + "_" + str(rho)],
                    menu_option=menu_option,
                    sector=sector_short,
                )
                df_scghg_expanded = df_scghg.expand_dims(
                    ["discount_rate", "menu_option", "sector"]
                )
                if "simulation" in df_scghg_expanded.dims:
                    df_scghg_expanded = df_scghg_expanded.drop_vars("simulation")
                all_arrays_uscghg = all_arrays_uscghg + [df_scghg_expanded]

                # For global consumption no pulse
                df_gcnp = df_single_gcnp.assign_coords(
                    discount_rate=discount_conversion_dict[str(eta) + "_" + str(rho)],
                    menu_option=menu_option,
                    sector=sector_short,
                )
                df_gcnp_expanded = df_gcnp.expand_dims(
                    ["discount_rate", "menu_option", "sector"]
                )
                if "simulation" in df_gcnp_expanded.dims:
                    df_gcnp_expanded = df_gcnp_expanded.drop_vars("simulation")
                all_arrays_gcnp = all_arrays_gcnp + [df_gcnp_expanded]

            attrs = merge_meta(attrs, meta)

            print("Processing...")
            df_full_scghg = xr.combine_by_coords(all_arrays_uscghg)
            df_full_gcnp = xr.combine_by_coords(all_arrays_gcnp)

            # Changes coordinate names of gases
            df_full_scghg = df_full_scghg.assign_coords(
                gas=[gas_conversion_dict[gas] for gas in df_full_scghg.gas.values]
            )

            # Splits SCGHGs by gas and saves them out separately
            # For uncollapsed SCGHGs
            if conf_name != "generated_conf.yml":
                conf_savename = re.split("\.", conf_name)[0] + "-"
            else:
                conf_savename = ""
            gases = conf["rff_climate"]["gases"]
            if uncollapsed:
                for gas in gases:
                    out_dir = (
                        Path(conf["save_path"])
                        / f"{'territorial_us' if terr_us else 'global'}_scghgs"
                        / "full_distributions"
                        / gas
                    )
                    makedir(out_dir)
                    uncollapsed_gas_scghgs = (
                        df_full_scghg.sel(gas=gas_conversion_dict[gas], drop=True)
                        .to_dataframe()
                        .reindex()
                    )
                    print(
                        f"Saving {'territorial U.S.' if terr_us else 'global'} uncollapsed {sector_short} sc-{gas} \n pulse year: {pulse_year}"
                    )
                    uncollapsed_gas_scghgs.to_csv(
                        out_dir
                        / f"{conf_savename}sc-{gas}-dscim-{menu_option}-{sector_short}-{pulse_year}-n10000.csv"
                    )
                    attrs_save = attrs.copy()
                    attrs_save["gases"] = gas
                    with open(
                        out_dir / f"{conf_savename}attributes-{gas}-{sector_short}.txt",
                        "w",
                    ) as f:
                        for key, value in attrs_save.items():
                            f.write("%s:%s\n" % (key, value))

            # Applies the adjustment factor to convert to certainty equivalent SCGHGs
            df_full_scghg = (
                df_full_scghg.adjustment_factor * df_full_scghg.scghg
            ).mean(dim="runid")

            # Splits and saves collapsed SCGHGs
            for gas in gases:
                out_dir = (
                    Path(conf["save_path"])
                    / f"{'territorial_us' if terr_us else 'global'}_scghgs"
                )
                makedir(out_dir)
                collapsed_gas_scghg = (
                    df_full_scghg.sel(gas=gas_conversion_dict[gas], drop=True)
                    .rename("scghg")
                    .to_dataframe()
                    .reindex()
                )
                print(
                    f"Saving {'territorial U.S.' if terr_us else 'global'} collapsed {sector_short} sc-{gas} \n pulse year: {pulse_year}"
                )
                collapsed_gas_scghg.to_csv(
                    out_dir
                    / f"{conf_savename}sc-{gas}-dscim-{menu_option}-{sector_short}-{pulse_year}.csv"
                )

            # Creates attribute files
            with open(
                out_dir / f"{conf_savename}attributes-{sector_short}.txt", "w"
            ) as f:
                for key, value in attrs.items():
                    f.write("%s:%s\n" % (key, value))

            # save global consumption no pulse for each sector. Does not vary by pulse_year
            if pulse_year == pulse_years[0]:
                # Fewer GCNPs are saved because they vary across fewer dimensions than SCGHGs
                if gcnp:
                    out_dir = Path(conf["save_path"]) / "gcnp"
                    makedir(out_dir)
                    df_full_gcnp.attrs = attrs
                    print(f"Saving {sector_short} global consumption no pulse (gcnp)")
                    df_full_gcnp.to_netcdf(
                        out_dir / f"{conf_savename}gcnp-dscim-{sector_short}.nc4"
                    )
                    print(f"gcnp is available in {str(out_dir)}")

    print(
        f"{'territorial_us' if terr_us else 'global'}_scghgs are available in {str(Path(conf['save_path']))}/{'territorial_us' if terr_us else 'global'}_scghgs"
    )
    if uncollapsed:
        print(
            f"Full distributions of {'territorial_us' if terr_us else 'global'}_scghgs are available in {str(Path(conf['save_path']))}/{'territorial_us' if terr_us else 'global'}_scghgs/full_distributions"
        )
