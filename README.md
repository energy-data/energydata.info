# Contributing

## Requirements

- [VirtualBox 5](http://virtualbox.org)
- [Vagrant](https://www.vagrantup.com/)
- This repo

## Development

### Initial provisioning
1. Clone this repo
2. `git submodule update --init --recursive` 
2. Copy `development.ini.sample` to `development.ini`
3. Change variables in development.ini:
   - beaker.session.secret
   - app.instance.uuid
   - ckanext.s3.*
   - Configure smtp for email
4. Start the VM with `vagrant up`
5. `vagrant ssh` to ssh into the VM
6. `source venv/bin/activate` which will allow you to use the datacats command
7. `cd /vagrant`
8. `datacats init` to initialize the environment and choose an admin password

### Booting
1. In the repo directory `vagrant up`. 
2. Point your web browser to 192.168.101.99 (the address of the VM)
3. Modifications to the CSS & templates will be reloaded automatically using vagrant sync. Adding templates or changing configuration files will not cause a server restart, check the next section to restart the server

### Restarting the server

If you're adding new templates or new functionality to CKAN, you might need to restart the CKAN server.

1. `vagrant ssh` to ssh into the VM
2. `source venv/bin/activate` which will allow you to use the datacats command
3. `cd /vagrant` (this is the synced folder with the git repo)
4. `datacats reload` to reload the server

### Styles (Less)

Less is compiled in the local machine, not vagrant.
The resulting styles should be committed to the repo.
 
#### Requirements

- Node (v4.2.x) & Npm ([nvm](https://github.com/creationix/nvm) usage is advised)

> The versions mentioned are the ones used during development. It could work with newer ones.

After these basic requirements are met, run the following commands in the website's folder:
```
npm install
```

#### Watch for changes

```
npm run less-watch
```
Starts the watcher and recompiles when files change.


## Deploy instructions
This assumes a base OS of Ubuntu 16.04

1. Clone this repo on the target machine
2. Follow the instructions in `build-box/build_box.sh`, changing `vagrant` to this repository's source directory
3. Copy `development.ini.sample` to `development.ini`
4. Change variables in development.ini:
   - beaker.session.secret
   - app.instance.uuid
   - ckanext.s3.*
   - Configure smtp for email
5. `cd wbg-energydata`
6. `datacats init` and choose an admin password
7. `datacats reload`
8. `datacats paster -d celeryd`
9. For HTTPS, install Let's Encrypt and uncomment the HTTPS section of the nginx configuration

### New iteration
To deploy a new iteration of the data platform to the production environment, follow these steps:

1. ssh into the machine
2. `cd wbg-energydata`
3. `git checkout master`
4. `git pull origin master`
5. [only if you enable a new plugin] `datacats install`
6. `datacats reload`
7. `datacats paster -d celeryd`
