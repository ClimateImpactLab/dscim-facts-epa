File formats
------------

Formatting your control/pulse input files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Depending on your DSCIM-FACTS-EPA run, you may need to format GMST, GMSL, or OHC control/pulse files.

.. _GMST:

Formatting GMST control/pulse file
""""""""""""""""""""""""""""""""""

To format your GMST, file you will 

.. image:: images/gmst.png

.. _GMSL:

Formatting GMSL control/pulse file
""""""""""""""""""""""""""""""""""

To format your GMSL, file you will 

.. image:: images/gmsl.png

.. _OHC:

Formatting OHC control/pulse file
"""""""""""""""""""""""""""""""""

To format your OHC, file you will 

.. image:: images/ohc.png

.. _config:

Modifying config files
"""""""""""""""""""""""

By default, :code:`dscim-facts-epa` includes a :code:`generated_conf.yml` file which can be used to generate 'default' SC-GHGs (CO2, CH4, and N2O) that replicate the EPA's September 2022 draft technical report. The alternative run processes specify the means to create custom configs that have alternative GMST and GMSL files. Once the custom config is created, the final step is to specify the "pulse conversion" for each gas. This conversion factor converts the final SC-GHG from :code:`$ / pulse size of FaIR gas species` to :code:`$ / tonne of GHG`. 

To do this, modify the `gas_conversions` portion of the config. By default, this is:

.. code-block:: yaml
    gas_conversions:
    CH4: 2.5e-08
    CO2_Fossil: 2.72916487e-10
    N2O: 6.36480131e-07

To add additional gases, create a new line and follow the formatting of the previous lines. New gases should match the coordinate values of your `gas` dimension in your gmst, gmsl, or ohc files. For example, the SCC default pulse size in DSCIM-FACTS-EPA is 1 GtC (1 gigatonne Carbon). To convert to $ / tonne CO2, molecular weights are used to convert C to CO2, and Gt is converted to tonnes: 

.. math::
    \frac{1}{((12+2*16)/12)} \times \frac{1}{1e9} = 2.72916487e-10
