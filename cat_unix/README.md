# Build My Own Unix cat Tool (cccat)

In this code I build my own **cccat** tool that is a recreation of unix **cat** tool; using *Python*.
It can read contents from file[s] or from standard in and print on the standard output.

This piece of code is based on this coding challenge: [Building Your Own cat Tool](https://codingchallenges.fyi/challenges/challenge-cat).

### Installation
##### step 1
Clone the project:
```commandline
git clone https://github.com/sarah-amiri/BuildingMyOwnTools.git
```
##### step 2
Go to its directory:
```commandline
cd cat_unix/
```
##### step 3
Make a virtual environment and activate it:
```commandline
python3 -m venv venv
source venv/bin/activate
```
##### step 4
Run the app with its script file or by installing packages through `setup.py`:
```commandline
[script]
python app/main.py

[package]
pip install .
cccat
```

### Options
You can also print line number using `-n` argument. It is optional.