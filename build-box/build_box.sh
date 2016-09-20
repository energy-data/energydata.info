export DEBIAN_FRONTEND=noninteractive


# Install git
echo "Installing git"
sudo apt-get update
sudo apt-get install -y git
mkdir -p ~/.ssh
chmod 700 ~/.ssh
ssh-keyscan -H github.com >> ~/.ssh/known_hosts

# Install guest additions
sudo apt-get install -y linux-headers-$(uname -r) build-essential dkms apt-transport-https

# Install python
echo "Installing python requirements"
sudo apt-get install -y python-pip python-dev build-essential
sudo pip install --upgrade pip
sudo pip install virtualenv

# Install datacats
echo "Installing datacats"
virtualenv venv
source venv/bin/activate
git clone https://github.com/developmentseed/datacats.git
cd datacats
python setup.py develop

# Install docker
echo "Installing docker"
sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
echo "deb https://apt.dockerproject.org/repo ubuntu-xenial main" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt-get update
sudo apt-get purge lxc-docker
apt-cache policy docker-engine
sudo apt-get install -y docker-engine
sudo usermod -aG docker $(whoami)
newgrp docker

# Build docker images
source ../venv/bin/activate
datacats pull
cd docker
sudo docker build -t devseed/datacats-shell shell/

# Install nginx and configure site
sudo apt-get install -y nginx
cp /vagrant/nginx.conf /etc/nginx/sites-available/default
sudo service nginx restart

