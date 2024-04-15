# FACTS troubleshooting:

<details>

<summary><b>FACTS hangs after "Setting up ZMQ queues"</b></summary>

Problem: 

When running FACTS, the output messages stop after "Setting up ZMQ queues" and FACTS seems to hang.

Potential Solution:

FACTS (specifically `radical`, the engine underlying FACTS) sets up its own virtual environment as a part of the run process. Some systems have specific versions of applications that cause the installation to fail. It is a known issue in `radical` that this failure will cause FACTS to hang. To check if this virtual environment has failed to install, wherever you are running FACTS (docker container or on your linux machine), find the default location of the engine at 

```
~/radical.pilot.sandbox/ve.local.localhost.<RADICAL.ENTK VERSION>
```

Make sure to record the exact path to the virtual environment, as we will recreate the environment in the same location shortly. In this folder, there should be a file:

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

We now need to install some packages into this new environment so it runs correctly. Make sure that you deactivate the conda environment or python environment before activating the new environment:

<details>

<summary><b>conda environment/ not docker</b></summary>

```bash
conda deactivate
. ~/radical.pilot.sandbox/ve.local.localhost.<RADICAL.ENTK VERSION>/bin/activate
```

Then install the packages:

```bash
pip install setuptools==69.0.2 radical.entk==1.42.0 radical.pilot==1.47.0 radical.utils==1.47.0 radical.saga==1.47.0 radical.gtod==1.47.0
```
With the packages installed, deactivate this environment and activate your run environment again:

```bash
deactivate
conda activate dscim-facts-epa
```

</details>

or if you are running in the docker container:

<details>

<summary><b>docker container</b></summary>

```bash
deactivate
. ~/radical.pilot.sandbox/ve.local.localhost.<RADICAL.ENTK VERSION>/bin/activate
```

Then install the packages:

```bash
pip install setuptools==69.0.2 radical.entk==1.42.0 radical.pilot==1.47.0 radical.utils==1.47.0 radical.saga==1.47.0 radical.gtod==1.47.0
```
With the packages installed, deactivate this environment and activate your run environment again:
```bash
deactivate
. /factsVe/bin/activate
```

</details>

Now you are ready to run the `facts_runs.sh` script again.

</details>

<details>

<summary><b>FACTS crashes shortly after "Setting up ZMQ queues"</b></summary>

Problem: 

When running FACTS, the run fails shortly after the output message "Setting up ZMQ queues". Initial exceptions in the stack trace vary but usually the stack trace ends with something like:
```
The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "runFACTS.py", line 193, in <module>
    run_experiment(args.edir, args.debug, args.alt_id, resourcedir=args.resourcedir, makeshellscript = args.shellscript, globalopts = args.global_options)
  File "runFACTS.py", line 86, in run_experiment
    amgr.run()
  File "/usr/local/lib/python3.8/dist-packages/radical/entk/appman/appmanager.py", line 485, in run
    raise EnTKError(ex) from ex
radical.entk.exceptions.EnTKError
```

Potential Solution: 

FACTS (specifically `radical`, the engine underlying FACTS) sets up its own virtual environment as a part of the run process. If FACTS crashes, it may be because this environment has failed to install some packages. Sometimes recreating this environment manually is necessary. Wherever you are running FACTS (docker container or on your linux machine), locate the environment, usually located:

```
~/radical.pilot.sandbox/ve.local.localhost.<RADICAL.ENTK VERSION>
```

Make sure to record the exact path to the virtual environment, as we will recreate the environment in the same location shortly. Delete the old environment then make the new one with the following commands:

```bash
rm -r ~/radical.pilot.sandbox/ve.local.localhost.<RADICAL.ENTK VERSION>
python3 -m venv ~/radical.pilot.sandbox/ve.local.localhost.<RADICAL.ENTK VERSION>
```

To verify that the environment has built properly, make sure `activate` is in the bin subdirectory of the virtual environment.

```bash
ls ~/radical.pilot.sandbox/ve.local.localhost.<RADICAL.ENTK VERSION>/bin/
```

We now need to install some packages into this new environment so it runs correctly. Make sure that your run environment before activating the new environment:

<details>

<summary><b>conda environment/ not docker</b></summary>

```bash
conda deactivate
. ~/radical.pilot.sandbox/ve.local.localhost.<RADICAL.ENTK VERSION>/bin/activate
```

Then install the packages:

```bash
pip install setuptools==69.0.2 radical.entk==1.42.0 radical.pilot==1.47.0 radical.utils==1.47.0 radical.saga==1.47.0 radical.gtod==1.47.0
```

With the packages installed, deactivate this environment and activate your run environment again:

```bash
deactivate
conda activate dscim-facts-epa
```

</details>

or if you are running in the docker container:

<details>

<summary><b>docker container</b></summary>

```bash
deactivate
. ~/radical.pilot.sandbox/ve.local.localhost.<RADICAL.ENTK VERSION>/bin/activate
```

Then install the packages:

```bash
pip install setuptools==69.0.2 radical.entk==1.42.0 radical.pilot==1.47.0 radical.utils==1.47.0 radical.saga==1.47.0 radical.gtod==1.47.0
```

With the packages installed, deactivate this environment and activate your run environment again:

```bash
deactivate
. /factsVe/bin/activate
```

</details>


Now you are ready to run the `facts_runs.sh` script again.

</details>

<details>

<summary><b>FACTS prints error messages the first time it is run</b></summary>

Problem:

When FACTS is first run, it starts printing messages related to modules being successfully completed, but suddenly begins printing one or more error messages.

Potential solution:

Sometimes when FACTS is first run in a new environment, it steps on its own toes by attempting to install the same package (or a package and its dependancy) on separate cores. This can cause FACTS to start printing error messages. Force stopping this run (or waiting for it to stop) and immediately running FACTS again (via the `bash facts_runs.sh` command) without changing anything else often resolves this issue.

</details>
