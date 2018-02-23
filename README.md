# ET_Flask
A web tool for deploying a materials science simulation model

# Description
This tool was developed due to the need by different people in my research group with no prior experience to the **Python** language and environment to access a materials science simulation model easily without the need to have to setup and understand the programmin code.
The simulation model code itself was developed at another research institution and thus has not been included in this repository.

## Use
The simulation model operating principle is to ask for input values from the user, and calculate the corresponding response. There are several input parameters that the model need to be executed and therefore the webpages ask specifically for all of these.
Once the user has provided all the input parameters for each case wanted to be simulated, the back-end code runs the model and the provides the responses as a file for the user to download.

# Installation
The web tool was written in **python3**, and employs **Flask** to create the web tool, and **gunicorn** and **nginx** as a `wsgi` `HTTP` web server. It is being run on a AWS EC2 t2.micro instance with Linux Ubuntu OS and uses `systemmd` as system manager to keep the server up and running.

To install the needed sofware, run:
```
$ sudo apt-get dist-upgrade
$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo apt autoremove
$ sudo apt-get install python3-pip python3-dev build-essential nginx
```

A reboot of the system may be needed and is suggested at this point.
Next, in order to install the different pieces of the tool, the **public IP** address of the server needs to be set in the environment for the server to configure its settings:
```
$ export IP=x.x.x.x
```

Now, run the `sudo install.sh` shell script that will install all needed dependencies and packages into the system. It will add a virtual environment through `virtualenv`, and create all needed files and libraries. If the installer does not work, please execute step by step the commands within that shell file.

The tool should then be available on any web browser at the public IP of the server.

**NOTE:** The web tool won't work properly until the simulation code source file `EagarTsai.py` is within the directory. If you would like to fully try this out, you may contact me to discuss how this code can be shared.
