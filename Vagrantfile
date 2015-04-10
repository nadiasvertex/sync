# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.
  config.vm.box = "ubuntu/trusty64"

  config.vm.define "db1" do |db1|
    db1.vm.box = "ubuntu/precise64"
    db1.vm.network "private_network", ip: "192.168.33.10"
    db1.vm.provision :shell, path: "bootstrap-db1.sh"
  end

  config.vm.define "db2" do |db2|
    db2.vm.box = "ubuntu/precise64"
    db2.vm.network "private_network", ip: "192.168.33.11"
    db2.vm.provision :shell, path: "bootstrap-db2.sh"
  end

  config.vm.define "db3" do |db3|
    db3.vm.box = "ubuntu/precise64"
    db3.vm.network "private_network", ip: "192.168.33.12"
    db3.vm.provision :shell, path: "bootstrap-db3.sh"
  end

  config.vm.define "web1" do |web1|
    web1.vm.network "private_network", ip: "192.168.33.20"
    web1.vm.provision :shell, path: "bootstrap-web.sh"
  end

  config.vm.define "web2" do |web2|
    web2.vm.network "private_network", ip: "192.168.33.21"
    web2.vm.provision :shell, path: "bootstrap-web.sh"
  end

  config.vm.define "web3" do |web3|
    web3.vm.network "private_network", ip: "192.168.33.22"
    web3.vm.provision :shell, path: "bootstrap-web.sh"
  end

  config.vm.define "lb", primary: true do |lb|
    lb.vm.network "private_network", ip: "192.168.33.5"
    lb.vm.network "forwarded_port", guest: 80, host: 8080
    lb.vm.provision :shell, path: "bootstrap-lb.sh"
  end

  config.vm.provider "virtualbox" do |vb|
     # Customize the amount of memory on the VM:
     vb.memory = "512"
  end
end
