Vagrant.configure("2") do |config|
	config.vm.box = "ubuntu/trusty32”
	config.vm.boot_timeout = 900
	config.vm.provision :shell, path: "bootstrap.sh"
	config.vm.provider “virtualbox” do |vb|
		vb.customize [“modifyvm”, :id, “—-nictype”, “Am79C973”]
	end
	config.vm.network “public_network”
	config.vm.synced_folder “C:\ChassisInfoFetcher\CIF", "/home/ubuntu/ChassisInfoFetcher"

end