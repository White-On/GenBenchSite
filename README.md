# BenchSite
A BenchMark project to compare differents library

## Seting the python Environment 

you'll need to add the library that will be compare. If not, the test won't run and the only result will be error 
inside the main file, create a virtual environment for python and run the following command to install the 
dependency required within *requirement.txt*.

`python -m venv venv`

`venv/Script/activate.bat`

`pip install -r requirement.txt`

If you don't want to use the venv, the only library required to run the project are:
- psutil
- numpy
- Pygments
- Jinja2
- tqdm 

and completed by the library you want to benchmark.
