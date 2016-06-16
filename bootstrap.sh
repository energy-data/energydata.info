export DEBIAN_FRONTEND=noninteractive

# Load the docker files
source venv/bin/activate
cd /vagrant
datacats install
datacats reload
