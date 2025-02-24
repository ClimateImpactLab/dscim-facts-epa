from pathlib import Path
from pyfiglet import Figlet
import os
from scghg_utils import read_replace_conf, epa_scghgs, VERSION


if __name__ == "__main__":

    ####################
    # EDIT path and filename to config if necessary.
    # Path to the config for this run. Default is "current working directory", cwd
    conf_name = "generated_conf.yml"
    fullpath = Path(os.getcwd()) / conf_name
    conf = read_replace_conf(fullpath)

    ####################
    # EDIT these parameters:
    
    # Which sectors to save out from: 
    # "combined", "coastal", "agriculture", "mortality", "energy", "labor",
    sectors = [
        "combined",
        "coastal",
        "agriculture",
        "mortality",
        "energy",
        "labor",
    ]

    # Risk options to save out
    risk_options = ["risk_aversion", "risk_neutral", ]

    # Pulse years to save out
    # pulse years should be present in climate files
    pulse_years = [
        2020,
        2030,
        2040,
        2050,
    ]

    # Target discount rates from:
    # "1.5% Ramsey", "2.0% Ramsey", "2.5% Ramsey",
    target_disc = [
        "1.5% Ramsey",
        "2.0% Ramsey",
        "2.5% Ramsey",
    ]

    # List of whether to run Global/Territory US SCGHGs
    # Can be "global", "terr_us", or both
    domains = ["global",]
    
    # Whether to save out global consumption no pulse
    gcnp = True

    # Whether to save out uncollapsed SCGHGs
    uncollapsed = True
    ####################

    coastal_v = str(conf["coastal_version"])
    mortality_v = str(conf["mortality_version"])
    CAMEL_v = f"CAMEL_m{mortality_v}_c{coastal_v}"

    sector = []
    for sec in sectors:
        if sec == "combined":
            sector.append(CAMEL_v)
        elif sec == "coastal":
            sector.append("coastal_v" + coastal_v)
        elif sec == "mortality":
            sector.append("mortality_v" + mortality_v)
        else:
            sector.append(sec)
    
    domains_ls = []
    for dom in domains:
        if dom == "terr_us":
            domains_ls.append(True)
        elif dom == "global":
            domains_ls.append(False)
        else:
            raise ValueError("Invalid choice for domains, values in list should be \"terr_us\" or \"global\"")

    eta_rho_conversion_dict = {
        "1.5% Ramsey": [1.016010255, 9.149608e-05],
        "2.0% Ramsey": [1.244459066, 0.00197263997],
        "2.5% Ramsey": [1.421158116, 0.00461878399],
    }

    etas_rhos = []
    for er in target_disc:
        if er in eta_rho_conversion_dict:
            etas_rhos.append(eta_rho_conversion_dict[er])
        else:
            raise ValueError("Invalid etas_rhos selection")

    gas_conversion_dict = {"CO2_Fossil": "CO2", "N2O": "N2O", "CH4": "CH4"}

    for gas in conf["gas_conversions"].keys():
        if gas not in gas_conversion_dict.keys():
            gas_conversion_dict[gas] = gas

    f = Figlet(font="slant", width=100)
    print(f.renderText("DSCIM"))
    print(f"... dscim-facts-epa version {VERSION} ...")

    if len(etas_rhos) == 0:
        raise ValueError("You must select at least one eta, rho combination")

    risk_combos = [[ro, "euler_ramsey"] for ro in risk_options]
 
    for dom in domains_ls:
        locale = "Territory US" if dom else "Global"
        print("=========================")
        print(f"Generating {locale} SCCs")
        print("=========================")
        print("")
        if dom:
            sector = [i + "_USA" for i in sector]
        epa_scghgs(
            sector,
            conf,
            conf_name,
            gas_conversion_dict,
            dom,
            etas_rhos,
            risk_combos,
            pulse_years=pulse_years,
            gcnp=gcnp,
            uncollapsed=uncollapsed,
        )
    print(f"All results are available in {str(Path(conf['save_path']))}")
