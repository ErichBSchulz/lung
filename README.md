# lung
Lung and Ventilation Models to support the [VentOS project](https://docs.google.com/document/d/1zuPdXqJ_gFg4drvJkdByst1vagz60usFGL3S3l_cO4A/edit?usp=sharing).

Broadly the notebooks, and python codes, provide the following functionality:

* [a rudimentary lung and ventilator model](ventos/sim/simple.py) [[notebook](plots.iyynb)] (currently only capable of generating PCV traces)
* [code for generating test traces](ventos/test_traces.py) [[demo notebook](test_traces.iyynb)], complete with noise, and mocking of signals from dual pressure and flow sensors. The `test_traces.py` script is executable from the command line and will repulate [a set of JSON files and plots](test_traces/) illustrating potential test cases.
* [applying signal processing filters to test traces](ventos/signal.py) [[notebook](lung.iyynb)]

## notes to self

This is the standard python nomenclature for packaging:

* modules: named by filenames (lowercase, with underscores)
* packages: named by their directory name (lowercase, without underscores)


