# FACTS troubleshooting:

<details>

<summary><b>FACTS hangs after "Setting up ZMQ queues"</b></summary>

FACTS (specifically `radical`, the engine underlying FACTS) sets up its own virtual environment as a part of the run process. Some systems have specific versions of applications that cause the installation to fail. It is a known issue in `radical` that this failure will cause FACTS to hang. To check if this virtual environment has failed to install, find the default location of the engine at 

```
~/radical.pilot.sandbox/ve.local.localhost.<RADICAL.ENTK VERSION>
```

In this folder, there should be a file:

```
~/radical.pilot.sandbox/ve.local.localhost.<RADICAL.ENTK VERSION>/bin/activate
```

If this file does not exist, you may have to manually create the virtual environment. First delete the old environment then make the new one with the following commands:

```bash
rm -r ~/radical.pilot.sandbox/ve.local.localhost.<RADICAL.ENTK VERSION>
python3 -m venv ~/radical.pilot.sandbox/ve.local.localhost.<RADICAL.ENTK VERSION>
```

Now the file that was missing before should exist. To verify, make sure `activate` is in the bin subdirectory of the virtual environment.

```bash
ls ~/radical.pilot.sandbox/ve.local.localhost.<RADICAL.ENTK VERSION>/bin/
```

We now need to install some packages into this new environment so it runs correctly. Make sure that you deactivate the conda environment before activating the new environment:

```bash
conda deactivate
. ~/radical.pilot.sandbox/ve.local.localhost.<RADICAL.ENTK VERSION>/bin/activate
```

Then install the packages:

```bash
pip install radical.entk==1.42.0 radical.pilot==1.47.0 radical.utils==1.47.0 radical.saga==1.47.0 radical.gtod==1.47.0
```

With the packages installed, deactivate this environment and activate your conda environment again:

```
deactivate
conda activate dscim-facts-epa
```

Now you are ready to run FACTS again.

</details>