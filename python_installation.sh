#!/bin/bash
# If you desire to set up another python version
    # -> Edit the python version distribution and version number exported below
    # -> Edit the python version check at the end of the file

export DISTRIBUTION_NUMBER="3.9.10"
export VERSION_NUMBER="3.9"

cd ~

sudo apt update
sudo apt-get update

sudo apt-get install libssl-dev openssl make gcc libffi-dev

cd /opt
sudo wget https://www.python.org/ftp/python/$DISTRIBUTION_NUMBER/Python-$DISTRIBUTION_NUMBER.tgz
sudo tar xzvf Python-$DISTRIBUTION_NUMBER.tgz
cd Python-$DISTRIBUTION_NUMBER
./configure --enable-loadable-sqlite-extensions --enable-optimizations
sudo make
sudo make install

sudo ln -fs /opt/Python-$DISTRIBUTION_NUMBER/Python /usr/bin/python$VERSION_NUMBER

python3.9 --version