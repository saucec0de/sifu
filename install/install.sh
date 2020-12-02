#!/bin/bash

# Base Linux Packages
sudo apt install -y vim
sudo apt install -y curl
sudo apt install -y gitk
sudo apt install -y python3-pip
sudo apt install -y make
sudo apt install -y libcap-dev
sudo apt install -y cppcheck
sudo apt install -y jq
sudo apt install -y expect
sudo apt install -y cflow

# Podman
sudo apt -y  install software-properties-common

# seems like old repo is deprecated for 20.04
if [[ "$(lsb_release -rs)"=="20.04" ]];
then
echo 'deb http://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_20.04/ /' | sudo tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list
curl -fsSL https://download.opensuse.org/repositories/devel:kubic:libcontainers:stable/xUbuntu_20.04/Release.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/devel:kubic:libcontainers:stable.gpg > /dev/null
sudo apt update
else
sudo add-apt-repository -y ppa:projectatomic/ppa
fi

sudo apt -y install podman

sudo cp podman/registries.conf /etc/containers/registries.conf
sudo chown root:root /etc/containers/registries.conf
sudo chmod 0644 /etc/containers/registries.conf

# Base Python Libraries
pip3 install flask
pip3 install flask-login
pip3 install jinja2
pip3 install pyyaml
pip3 install passlib
pip3 install bcrypt
pip3 install regex
pip3 install tinydb
pip3 install xlsxwriter
pip3 install pexpect
pip3 install flask-web-log
pip3 install faker
pip3 install colored

# Additional Tools
pip3 install semgrep

# GCC-10 and CLANG-10
sudo add-apt-repository ppa:jonathonf/gcc-10.0
sudo apt install -y gcc-10
sudo apt install -y clang-10
sudo apt install -y g++-10
sudo apt install -y g++-10-multilib
sudo apt install -y gcc-10-multilib
sudo apt install -y clang-tidy-10

# Bubble-Wrap
sudo apt remove -y bubblewrap
wget https://github.com/containers/bubblewrap/archive/v0.4.0.tar.gz
tar xvzf v0.4.0.tar.gz
cd v0.4.0
./configure
make
sudo make install
rm -rf v0.4.0
popd
rm -rf v0.4.0

# FB-Infer
mkdir -p fbinfer
VERSION=0.17.0
curl -SL "https://github.com/facebook/infer/releases/download/v$VERSION/infer-linux64-v$VERSION.tar.xz" --output fbinfer/infer.tar.xz
sudo tar -C /opt -xvJf fbinfer/infer.tar.xz
sudo ln -s "/opt/infer-linux64-v$VERSION/bin/infer" /usr/local/bin/infer
rm -rf fbinfer

#### 
#### # PVS-Studio
#### mkdir -p pvs-studio
#### curl -SL "http://files.viva64.com/pvs-studio-7.05.35582.25-x86_64.tgz"  --output pvs-studio/pvs-studio-7.05.35582.25-x86_64.tgz
#### pushd pvs-studio
#### tar xvzf pvs-studio-7.05.35582.25-x86_64.tgz
#### cd pvs-studio-7.05.35582.25-x86_64
#### sudo ./install.sh
#### popd
#### rm -rf pvs-studio
#### 
# SonarQube: Main App
podman pull sonarqube

# SonarQube: sonar-scanner
curl -SL "https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.2.0.1873-linux.zip"  --output install/sonar-scanner-cli-4.2.0.1873-linux.zip
mkdir -p /opt/
mkdir sonarqube
pushd sonarqube
unzip sonar-scanner-cli-4.2.0.1873-linux.zip
sudo mv sonar-scanner-4.2.0.1873-linux /opt/
popd
rm -rf sonarqube
echo -e "PATH=\$PATH:/opt/sonar-scanner-4.2.0.1873-linux/bin" >> ~/.bashrc

# Java
sudo apt install -y default-jdk visualvm
sudo apt install -y maven

