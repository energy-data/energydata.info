# -*- mode: ruby -*-
# vim: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "devseed-datacats"
  config.vm.box_url = "https://s3.amazonaws.com/offgrid-vbox/devseed-datacats.box"

  config.ssh.forward_agent = true
  config.vm.network "private_network", ip: "192.168.101.99"


  config.vm.provider "virtualbox" do |vb|
     vb.memory = "1024"
     vb.cpus = 2
  end

  config.vm.provision "shell", path: "bootstrap.sh"
end
