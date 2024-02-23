# Build My Own Unix wc Tool (ccwc)

In this code I build my own **ccwc** tool that is a recreation of unix **wc** tool using *Python*.
It can show number of bytes, characters, lines and words in a file or input. 

This piece of code is based on this coding challenge: [Building Your Own wc Tool](https://codingchallenges.fyi/challenges/challenge-wc).

### Installation
##### step 1
Clone the project:
```commandline
git clone https://github.com/sarah-amiri/BuildingMyOwnTools.git
```
##### step 2
To run *ccwc* app go to its directory:
```commandline
cd unix_wc
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
ccwc
```

### Options
When running this app, several optional arguments are available. You can see a list of these options using `--help` command.