#!/bin/bash

#download virtualenv
sudo pip3 install virtualenv

#make sure to place the enviroment directory in the same folder
DIR="$( cd "$(dirname "${BASH_SOURCE[@]}")" ; pwd -P )"
cd $DIR/
virtualenv -p python3 ET_ENV/

# install all packages and initialize the database
source ET_ENV/bin/activate
pip install --editable .
export FLASK_APP="ET_Flask.wsgi"
flask initdb
deactivate

#move files to systemd locations
sed -i.bak "s~\${DIR}~$DIR~g" ET_Flask.service
sed -i.bak -e "s~\${DIR}~$DIR~g" -e "s~\${IP}~$IP~g" ET_Flask.nginx
sudo cp ET_Flask.service /etc/systemd/system/
sudo cp ET_Flask.nginx /etc/nginx/sites-available/ET_Flask
sudo ln -s /etc/nginx/sites-available/ET_Flask /etc/nginx/sites-enabled
rm *.bak

#move shared library
cp $DIR/$(find build -name *.so) ET_Flask/

#start the services through systemd
sudo systemctl daemon-reload
sudo systemctl start ET_Flask
sudo systemctl enable ET_Flask
sudo systemctl restart nginx
sudo ufw allow 'Nginx Full'

#create temp folder
mkdir ET_Flask/tmp
