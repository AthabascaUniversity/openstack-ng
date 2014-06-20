PRIVATE_NET_ID=`neutron net-create private | awk '/ id / { print $4 }'`
PRIVATE_SUBNET1_ID=`neutron subnet-create --name private-subnet1 $PRIVATE_NET_ID 10.0.0.0/24 | awk '/ id / { print $4 }'`

# List network and subnet
neutron net-list
neutron subnet-list

# Examine details of network and subnet
neutron net-show $PRIVATE_NET_ID
neutron subnet-show $PRIVATE_SUBNET1_ID

cat >> ~/.bashrc <<EOF
export PRIVATE_NET_ID=$PRIVATE_NET_ID
export PRIVATE_SUBNET1_ID=$PRIVATE_SUBNET1_ID
EOF


# Boot an instance using flavor and image names (if names are unique)
nova boot --image cirros-qcow2 --flavor m1.tiny MyFirstInstance

# Boot an instance using flavor and image IDs
nova boot --image $IMAGE_ID_2 --flavor 1 MySecondInstance

# List instances, notice status of instance
nova list

# Show details of instance
nova show MyFirstInstance

# View console log of instance
nova console-log MyFirstInstance

# Update default security group to allow host access to guest subnet
nova secgroup-add-rule default icmp -1 -1 10.0.0.0/24
nova secgroup-add-rule default tcp 22 22 10.0.0.0/24

# Get network namespace (ie, qdhcp-5ab46e23-118a-4cad-9ca8-51d56a5b6b8c)
sudo ip netns
NETNS_ID=qdhcp-$PRIVATE_NET_ID

# Ping first instance after status is active
sudo ip netns exec $NETNS_ID ping -c 3 10.0.0.3

# Log into first instance ( username is 'cirros', password is 'cubswin:)' )
sudo ip netns exec $NETNS_ID ssh cirros@10.0.0.3

# If you get a 'REMOTE HOST IDENTIFICATION HAS CHANGED' warning from previous command
sudo ssh-keygen -f "/root/.ssh/known_hosts" -R 10.0.0.3

# Ping second instance from first instance
ping -c 3 10.0.0.4

# Log into second instance from first instance ( username is 'cirros', password is 'cubswin:)' )
ssh cirros@10.0.0.4


# Log out of second instance
exit

# Log out of first instance
exit

# Use virsh to talk directly to libvirt
sudo virsh list --all

# Delete instances
nova delete MyFirstInstance
nova delete MySecondInstance

# List instances, notice status of instance
nova list

cat >> ~/.bashrc <<EOF
export NETNS_ID=$NETNS_ID
EOF

