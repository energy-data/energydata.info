export DEBIAN_FRONTEND=noninteractive

# Install git
echo "Installing git"
sudo apt-get update
sudo apt-get install -y git
mkdir -p ~/.ssh
chmod 700 ~/.ssh
ssh-keyscan -H github.com >> ~/.ssh/known_hosts

# Install python
echo "Installing python requirements"
sudo apt-get install -y python-pip python-dev build-essential
sudo pip install --upgrade pip
sudo pip install virtualenv

# Install datacats
echo "Installing datacats"
virtualenv venv
source venv/bin/activate
git clone git@github.com:developmentseed/datacats.git
cd datacats
python setup.py develop

# Install docker
echo "Installing docker"
wget -qO- https://get.docker.com/ | sh
sudo usermod -aG docker $(whoami)
newgrp docker