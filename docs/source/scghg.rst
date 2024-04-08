.. _SCGHG:

Generating SC-GHGs
------------------

After setting up the dscim-facts-epa environment and input data, activate the environment by typing :code:`conda activate dscim-facts-epa`. You can run SC-GHG calculations under different conditions with or without a config file.

Assuming you are in the :code:`dscim-facts-epa/scripts` folder, if you want to run the cil-spec SC-GHGs, you can run:

.. code-block:: console

   python command_line_scghg.py


Alternatively, if you have run FACTS, or are using a gmsl file of your own, you can run:

.. code-block:: console

   python command_line_scghg.py name_of_config.yml


and follow the on-screen prompts. When the selector is a carrot, you may only select one option. Use the arrow keys on your keyboard to highlight your desired option and click enter to submit. When you are presented with :code:`X` and :code:`o` selectors, you may use the spacebar to select (`X`) or deselect (`o`) then click enter to submit once you have chosen your desired number of parameters. Once you have completed all of the options, the DSCIM run will begin.

Command line options
^^^^^^^^^^^^^^^^^^^^

Below is a short summary of what each command line option does. To view a more detailed description of what the run parameters do, see the `Documentation <https://impactlab.org/research/data-driven-spatial-climate-impact-model-user-manual-version-092023-epa/>`_ for Data-driven Spatial Climate Impact Model (DSCIM). 

Sector
^^^^^^

The user may only select one sector per run. Sectors represent the combined SC-GHG or partial SC-GHGs of the chosen sector.

Discount rate
^^^^^^^^^^^^^

These runs use endogenous Ramsey discounting that are targeted to begin at the chosen near-term discount rate(s). 

Pulse years
^^^^^^^^^^^

Pulse year represents the SC-GHG for a pulse of greenhouse gas (GHG) emitted in the chosen pulse year(s). 

Domain of damages
^^^^^^^^^^^^^^^^^

The default is a global SC-GHG accounting for global damages in response to a pulse of GHG. The user has the option to instead limit damages to those occurring directly within the territorial United States. This is only a partial accounting of the cost of climate change to U.S. citizens and residents because it excludes international transmission mechanisms, like trade, cross-border investment and migration, damage to the assets of U.S. citizens and residents outside the United States, or consideration of how GHG emission reduction activity within the United States impacts emissions in other countries.

Optional files
^^^^^^^^^^^^^^

By default, the script will produce the expected SC-GHGs as a :code:`.csv`. The user also has the option to save the full distribution of 10,000 SC-GHGs -- across emissions, socioeconomics, and climate uncertainty -- as a :code:`.csv`, and the option to save global consumption net of baseline climate damages (^global_consumption_no_pulse^) as a netcdf :code:`.nc4` file.
