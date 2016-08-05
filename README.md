# Contributing

## Requirements

- [VirtualBox 5](http://virtualbox.org)
- [Vagrant](https://www.vagrantup.com/)
- This repo

## Development

1. Clone this repo
2. Copy `development.ini.sample` to `development.ini`
3. In the repo directory `vagrant up`. This will download the VM built for this project and start the CKAN instance
4. Point your web browser to 192.168.101.99 (the address of the VM)
5. Modifications to the CSS & templates will be reloaded automatically using vagrant sync. Adding templates or changing configuration files will not cause a server restart, check the next section to restart the server

## Restarting the server

If you're adding new templates or new functionality to CKAN, you might need to restart the CKAN server.

1. `vagrant ssh` to ssh into the VM
2. `source venv/bin/activate` which will allow you to use the datacats command
3. `cd /vagrant` (this is the synced folder with the git repo)
4. `datacats reload` to reload the server

## Styles (Less)

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
To deploy a new version of the data platform to the production environment, follow these steps:

1. ssh into the machine
2. `cd wbg-energydata`
3. `git checkout master`
4. `git pull origin master`
5. [only if you enable a new plugin] `datacats install`
6. `datacats reload -p`
7. `datacats paster -d celeryd`
