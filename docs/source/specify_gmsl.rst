User specified GMST and GMSL
----------------------------

Formatting your files
^^^^^^^^^^^^^^^^^^^^^

To begin with, format your GMST and GMSL files:
 - :ref:`GMST`
 - :ref:`GMSL`

Generating a config
^^^^^^^^^^^^^^^^^^^

With your alternative GMSL and GMST files, it is recommended to run them through the `create_config.py`. This script will generate a config that will allow you to directly begin running `dscim-facts-epa` using the user-specified GMST and GMSL inputs, gases, and pulse_years. To run this script, you will need to specify your correctly formatted gmst and gmsl files:

.. code-block:: console

    python create_config.py \
        --gmst_file /path/to/GMST_filename.nc4 \
        --gmsl_file /path/to/GMSL_filename.nc4 \
        --pulse_years pulseyear1 pulseyear2 ... \
        --gases gas1 gas2 ... \
        --input_dir /path/to/dscim-facts-epa/input \
        --output_dir /path/to/dscim-facts-epa/output \
        --config_dir /path/to/dscim-facts-epa/configs

Description of arguments:
    - :code:`--gmst_file`: The path to your GMST file
    - :code:`--gmsl_file`: The path to your GMSL file
    - :code:`--pulse_years`  (optional -- default: 2020): Space delimited pulse years. Pulse years must be included in the coordinates of your gmst/gmsl files
    - :code:`--gases` (optional -- default: "CO2_Fossil"): Space delimited gases. Gases must be included in the coordinates of your gmst/gmsl files
    - :code:`--input_dir` (optional -- default: the :code:`dscim-facts-epa/scripts/input` that the :code:`config.py` script belongs to) path to the inputs that were installed from the :code:`directory_setup.py` script
    - :code:`--output_dir` (optional -- default: the :code:`dscim-facts-epa/scripts/output` that the :code:`config.py` script belongs to) path to the output directory where the SC-GHGs will be saved
    - :code:`--config_dir` (optional -- default: the same directory that the :code:`config.py` script belongs to) path to the save directory for the generated config

Once your config has been generated, proceed to the next step.

Modifying the generated config
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the previous step ran successfully, a custom config file has been generated as a result of the script. This config file must first be completed before SC-GHGs can be generated. To complete the config file, :ref:`follow this guide <config>`.

Running SC-GHGs
^^^^^^^^^^^^^^^

Finally, you are ready to generate SC-GHGs:

:ref:`SCGHG`