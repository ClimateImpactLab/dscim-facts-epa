Welcome to DSCIM documentation!
===============================

DSCIM: The Data-driven Spatial Climate Impact Model
---------------------------------------------------

This repository is an implementation of DSCIM, referred to as DSCIM-FACTS-EPA, that implements the SC-GHG specification for the U.S. Environmental Protection Agency’s (EPA) September 2022 draft technical report, "Report on the Social Cost of Greenhouse Gases: Estimates Incorporating Recent Scientific Advances", and includes the option to input exogenous global mean surface temperature (GMST) and global mean sea level (GMSL) trajectories. DSCIM-FACTS-EPA currently provides instructions for installing and running the Framework for Assessing Changes To Sea-level ([FACTS](https://github.com/radical-collaboration/facts)) to obtain GMSL from GMST.

This Python library enables the calculation of sector-specific partial social cost of greenhouse gases (SC-GHG) and SC-GHGs that are combined across sectors. The main purpose of this library is to parse the monetized spatial damages from different sectors and integrate them into SC-GHGs for different discount levels, pulse years, and greenhouse gases.

Installation and setup of `dscim-facts-epa`
-------------------------------------------

To begin, we assume you have a system with `conda` available from the command line, and some familiarity with it. A conda distribution is available from [miniconda](https://docs.conda.io/en/latest/miniconda.html), [Anaconda](https://www.anaconda.com/), or [mamba](https://mamba.readthedocs.io/en/latest/). This helps to ensure that required software packages are correctly compiled and installed, replicating the analysis environment. If you are using conda, we recommend following [this](https://www.anaconda.com/blog/a-faster-conda-for-a-growing-community) guide to speed up environment solve time.

Begin in the `dscim-facts-epa` project directory, which can be downloaded and unzipped, or cloned with `git` in a terminal. For example:

.. code-block:: console
   git clone https://github.com/ClimateImpactLab/dscim-facts-epa.git

Next, from within the root directory of `dscim-facts-epa`, set up a conda environment for this analysis. This replicates the software environment used for analysis. With `conda` from the command line this is

.. code-block:: console
   conda env create -f environment.yml


and then activate the environment with

.. code-block:: console
   conda activate dscim-facts-epa


Be sure that all commands and analyses are run from this conda environment.

With the environment set up and active, the next step is downloading the required DSCIM-FACTS-EPA input data into the local directory. Assuming you are in the `dscim-facts-epa/scripts` directory, from the command line run:

.. code-block:: console

   python directory_setup.py


Note that this will download several gigabytes of data and may take several minutes, depending on your connection speed.


Types of run cases
------------------

By default, DSCIM-FACTS-EPA can run SC-GHGs for carbon dioxide, methane, and nitrous oxide for pulse years 2020-2080 in 10 year increments for the Resources for the Future socioeconomic pathways (RFF-SPs). For alternative gases or pulse years, the user can provide new GMST and GMSL trajectories. The user can provide these trajectories directly as input files, or can use the DSCIM-FACTS-EPA FACTS runner to generate GMSL from ocean heat content (OHC) and GMST. The intended use cases of this repository are thus:

1. The user wants to generate the default Climate Impact Lab (CIL) RFF SC-GHGs.
2. The user has alternative GMST and GMSL files following the guidelines below and wants to use the CIL damage functions to generate SC-GHGs based on those files.
3. The user has alternative GMST and OHC files following the guidelines below (usually directly from a simple climate model, such as FaIR) and wants to generate GMSL files from FACTS and use the CIL damage functions to generate SC-GHGs from those files.

.. toctree::
   :maxdepth: 2

   default
   specify_gmsl
   facts_gmsl