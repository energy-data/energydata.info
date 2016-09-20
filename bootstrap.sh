export DEBIAN_FRONTEND=noninteractive

# Load the docker files
source venv/bin/activate
cd /vagrant


cat > .datacats-environment <<EOF
[datacats]
name = offgrid
ckan_version = 2.4

[deploy]
target = datacats@command.datacats.com

[site_primary]
port = 5102
site_url = http://192.168.101.99
EOF
