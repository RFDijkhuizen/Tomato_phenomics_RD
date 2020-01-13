# Tomato_phenomics_RD

This project is for automatically phenotyping plants and performing a QTL on their measured traits.
Although this script is optimised for two week old tomato plants there are machine learning modules attached that
can finetune the parameters to any plant as long as you have "true positives"

1. VIS_workflow.py
is the python script responsible for measuring the plants, mostly using plantcv. Simply input the files and
this script will output a .json output. The other _workflow scripts are outdated versions
2. Parameter_fitting_CIELAB.py
This is the machine learning script that is responsible for fitting the parameters to your plants. Input true positives
in which you made everything except the things you want to be considered plant white. This script will now output the correct
parameters to be used in VIS_workflow.py. These have to be manually copied to VIS_workflow.py. The other parameter_fitting
scripts are outdated versions.
3. VerweRRRking.R
Is the script which is responsible for looking at the results. Does currently not output anything except some pretty graphs.
