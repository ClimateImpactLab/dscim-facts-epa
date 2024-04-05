Generate GMSL by running GMST and OHC through FACTS
---------------------------------------------------

Formatting your files
^^^^^^^^^^^^^^^^^^^^^

To begin with, format your GMST and OHC files:
 - :ref:`GMST`
 - :ref:`OHC`

Setting up FACTS
^^^^^^^^^^^^^^^^

.. note::
   **If you are on a Windows machine**, you will need to `setup WSL2 <https://learn.microsoft.com/en-us/windows/wsl/install>`_ and run all of the following steps through Ubuntu. Once you have installed and setup WSL2, to launch Ubuntu go to your command prompt and type:

   .. code-block:: console

      ubuntu

1. We recommend installing or cloning FACTS v1.1.2 found `here <https://github.com/radical-collaboration/facts/releases/tag/v1.1.2>`_. 

2. To download the FACTS input files, navigate to the FACTS repository and wget the modules data. For DSCIM-FACTS-EPA, we only download the inputs needed for the global FACTS runs.

   .. code-block:: console

      wget -P modules-data -i modules-data/modules-data.global_only.urls.txt

3. We use the FACTS Docker to ensure replicability. First, `install Docker <https://docs.docker.com/get-docker/>`_ and launch Docker desktop. 

4. Build the docker container:

   .. code-block:: console

      cd facts/docker
      sh develop.sh
      
5. Start a container image from the :code:`facts` image. You will need to mount both the :code:`facts` repository as well as the :code:`dscim-facts-epa` repository in the FACTS docker. Replace :code:`/path/to` in the following with the locations of your :code:`facts` and :code:`dscim-facts-epa` repositories.  

   .. code-block:: console

      docker run -it \
       --volume=/path/to/facts:/opt/facts \
       --volume=/path/to/dscim-facts-epa:/opt/dscim-facts-epa -w /opt/dscim-facts-epa/scripts/facts.runs facts

You will now be in a container image in the :code:`/opt/dscim-facts-epa/scripts/facts.runs` directory. If you have done everything correctly up to this point, this directory will contain a few scripts, most notably :code:`facts_runs.sh`. In the next step, you will make modifications to this script.

Running FACTS
^^^^^^^^^^^^^

.. warning::
   Running FACTS is a relatively memory-intensive and disk-space-intensive process. To successfully run FACTS, you will need a moderately powerful workstation (or server) with at least 32 gigabytes of computer RAM. In addition, FACTS currently requires around 6 gigabytes of disk space per pulse year-gas, which means that 3 gases and 7 pulse years (a total of 22 runs including the control) will require approximately 132 gigabytes of disk space. Alternatively, one can run subsets of runs at a time and clear memory in between. To clear memory after a run has been completed, remove the subdirectories in the :code:`~/radical.pilot.sandbox` folder.

The user must now make modifications to the :code:`/opt/dscim-facts-epa/scripts/facts.runs/facts_runs.sh` script to ensure all files are found and run specifications are set. Those changes are:
 - if you want to rerun previous successful experiments (not recommended), change :code:`overwrite` to 1
 - on line 8 of the script, change :code:`pulse_years` to the desired pulse years to be run by FACTS
 - on line 9, change :code:`gas` to the desired gases to be run by FACTS
 - on line 11, change the path to the path of your GMST file
 - on line 12, change the path to the path of your OHC file
 - on line 14, change the path to the path of your GMSL file (where you want the GMSL file to be saved)
 
 If not running in the Docker Container:
 - on line 16, change :code:`facts_dir` to where you have cloned your FACTS repository
 - on line 17, change :code:`dscim_facts_epa_dir` to where you have cloned this repository 

Assuming you are in the :code:`dscim-facts-epa/scripts/facts.runs` folder run:

.. code-block:: console
   
   bash facts_runs.sh 

Note that the more pulse year and gas dimensions your input climate files have, the longer this run will take as pulse year-gas combinations are run in sequence. On a fast machine, each combination can take approximately 10 minutes, meaning that for a run of 3 gases for 7 pulse years, the run will take 220 minutes. The run script will create the appropriate number of FACTS "experiments" (22 in the example case), run through them, and concatenate the outputs into the format expected by :code:`dscim-facts-epa`. 

Modifying the auto-generated config
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If all of the prior steps have run successfully, this process will have created a file of control and pulse GMSL trajectories based on your GMST and OHC trajectories. Importantly, a config for the following SC-GHG runs has been created (the name of this config has been printed to the command line), and the paths to the appropriate inputs have been auto-populated in the config. This config file must first be completed before SC-GHGs can be generated. To complete the config file, :ref:`follow this guide <config>`.

Running SC-GHGs
^^^^^^^^^^^^^^^
