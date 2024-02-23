# Build My Own Webserver

In this piece of code, I built a simple web server using Python. Now, it only accepts *GET* requests and returns *HTML* page based on request path.

This piece of code is based on this coding challenge: [Building Your Own Web Server](https://codingchallenges.fyi/challenges/challenge-webserver).

### Installation
##### step 1
Clone the project:
```commandline
git clone https://github.com/sarah-amiri/BuildingMyOwnTools.git
```
##### step 2
To run *web server* app go to its directory:
```commandline
cd webserver
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
webserver 
```

### Arguments
You can specify port and host to run the webserver on by using `--port` and `--host` arguments. These arguments are optional and if not set, default values are used that are `localhost` for host and `3300` for port.