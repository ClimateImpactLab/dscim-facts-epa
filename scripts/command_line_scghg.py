import inquirer
from pathlib import Path
from pyfiglet import Figlet
import os
from scghg_utils import read_replace_conf, epa_scghgs, VERSION

if __name__ == "__main__":

    f = Figlet(font="slant", width=100)
    print(f.renderText("DSCIM"))
    print(f"... dscim-facts-epa version {VERSION} ...")

    # Path to the config for this run
    conf_name = "generated_conf.yml"
    master = Path(os.getcwd()) / conf_name
    conf = read_replace_conf(master)

    coastal_v = str(conf["coastal_version"])
    mortality_v = str(conf["mortality_version"])
    CAMEL_v = f"CAMEL_m{mortality_v}_c{coastal_v}"

    pulse_years = conf["rffdata"]["pulse_years"]
    pulse_year_choices = [(str(i), i) for i in pulse_years]
    questions = [
        inquirer.Checkbox(
            "menu_option",
            message="Select risk type (If choosing Risk Neutral, the only available sector is Combined)",
            choices=[
                ("Risk Aversion", "risk_aversion"),
                ("Risk Neutral", "risk_neutral"),
            ],
            default=[
                "risk_aversion",
            ],
        ),
        inquirer.Checkbox(
            "sector",
            message="Select sector",
            choices=[
                ("Combined", CAMEL_v),
                ("Coastal", "coastal_v" + coastal_v),
                ("Agriculture", "agriculture"),
                ("Mortality", "mortality_v" + mortality_v),
                ("Energy", "energy"),
                ("Labor", "labor"),
            ],
            default=[
                CAMEL_v,
                # "coastal_v" + coastal_v,
                # "agriculture",
                # "mortality_v" + mortality_v,
                # "energy",
                # "labor",
            ],
        ),
        inquirer.Checkbox(
            "eta_rhos",
            message="Select discount rates",
            choices=[
                ("1.5% Ramsey", [1.016010255, 9.149608e-05]),
                ("2.0% Ramsey", [1.244459066, 0.00197263997]),
                ("2.5% Ramsey", [1.421158116, 0.00461878399]),
            ],
            default=[
                [1.016010255, 9.149608e-05],
                [1.244459066, 0.00197263997],
                [1.421158116, 0.00461878399],
            ],
        ),
        inquirer.Checkbox(
            "pulse_year",
            message="Select pulse years",
            choices=pulse_year_choices,
            default=pulse_years,
        ),
        inquirer.Checkbox(
            "U.S.",
            message="Select valuation type",
            choices=[("Global", False), ("Territorial U.S.", True)],
            default=[False, 
                    #  True
                     ],
        ),
        inquirer.Checkbox(
            "files",
            message="Optional files to save (will increase runtime substantially)",
            choices=[
                ("Global consumption no pulse", "gcnp"),
                ("Uncollapsed scghgs", "uncollapsed"),
            ],
        ),
    ]

    answers = inquirer.prompt(questions)
    eta_rhos = answers["eta_rhos"]
    sector = answers["sector"]
    menu_options = answers["menu_option"]
    pulse_years = answers["pulse_year"]
    terr_us_ls = answers["U.S."]
    gcnp = True if "gcnp" in answers["files"] else False
    uncollapsed = True if "uncollapsed" in answers["files"] else False

    coastal_v = str(conf["coastal_version"])
    mortality_v = str(conf["mortality_version"])
    CAMEL_v = f"CAMEL_m{mortality_v}_c{coastal_v}"

    gas_conversion_dict = {"CO2_Fossil": "CO2", "N2O": "N2O", "CH4": "CH4"}

    for gas in conf["gas_conversions"].keys():
        if gas not in gas_conversion_dict.keys():
            gas_conversion_dict[gas] = gas

    risk_combos = [[mo, "euler_ramsey"] for mo in menu_options]

    for terr_us in terr_us_ls:
        locale = "Territory US" if terr_us else "Global"
        print("=========================")
        print(f"Generating {locale} SCCs")
        print("=========================")
        print("")
        if terr_us:
            sector = [i + "_USA" for i in sector]
        epa_scghgs(
            sector,
            conf,
            conf_name,
            gas_conversion_dict,
            terr_us,
            eta_rhos,
            risk_combos,
            pulse_years=pulse_years,
            gcnp=gcnp,
            uncollapsed=uncollapsed,
        )
    print(f"All results are available in {str(Path(conf['save_path']))}")
