# Start

sudo core-daemon

sudo core-gui

# Connect with Host

Under the Session Menu, the Options… dialog has an option to set a control network prefix.

This can be set to a network prefix such as 172.16.0.0/24. A bridge will be created on the host machine having the last address in the prefix range (e.g. 172.16.0.254), and each node will have an extra ctrl0 control interface configured with an address corresponding to its node number (e.g. 172.16.0.3 for n3.)

## Set Default

uncomment configuration line on /etc/core/core.conf and restart core-daemon. 
* Network .xml file can overwrite this config, so configure .xml file to. 

## Node -> Host

ping 172.16.0.254

## Host -> Node (n2)

ping 172.16.0.2

# Uninstall

cd <CORE_REPO>

sudo make uninstall

make clean

./bootstrap.sh clean

inv uninstall

pipx uninstall-all