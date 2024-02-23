# Build My Own JSONParser

In this piece of code, I built my own json parser using Python. It enters a `.json` file as argument and indicates it can be parsed as a json or not.

This piece of code is based on this coding challenge: [Building Your Own JSON Parser](https://codingchallenges.fyi/challenges/challenge-json-parser).

### Installation
##### step 1
Clone the project:
```commandline
git clone https://github.com/sarah-amiri/BuildingMyOwnTools.git
```
##### step 2
To run *json parser* app go to its directory:
```commandline
cd jsonparser
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
jsonparser <file_name>
```

### Arguments
You need to give file name as an argument when running this script. If file is not provided/exist, you will get an error.