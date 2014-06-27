get_id(){
 RET=$($@ | awk '/ id / {print $4; }')
 echo $RET
}

PRIVATE_NET_ID=$(get_id neutron net-create private )
PRIVATE_SUBNET1_ID=$(get_id neutron subnet-create --name private-subnet1 $PRIVATE_NET_ID 10.0.0.0/24 )

# List network and subnet
neutron net-list
neutron subnet-list

# Examine details of network and subnet
neutron net-show $PRIVATE_NET_ID
neutron subnet-show $PRIVATE_SUBNET1_ID

MY_PUBLIC_SUBNET_CIDR=192.168.0.0/24
PUBLIC_NET_ID=$(get_id neutron net-create public --router:external=True )
PUBLIC_SUBNET_ID=$(get_id neutron subnet-create --name public-subnet $PUBLIC_NET_ID $MY_PUBLIC_SUBNET_CIDR -- --enable_dhcp=False )

cat >> ~/.bashrc <<EOF
export PRIVATE_NET_ID=$PRIVATE_NET_ID
export PRIVATE_SUBNET1_ID=$PRIVATE_SUBNET1_ID
EOF

glance image-create --name cirros-qcow2 --container-format bare --disk-format qcow2 --file /tmp/images/cirros-0.3.2-x86_64-disk.img --is-public True

# Boot an instance using flavor and image names (if names are unique)
INSTANCE_ID=$(get_id nova boot --image cirros-qcow2 --flavor m1.tiny MyFirstInstance)

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
sudo ip netns list
NETNS_ID=qdhcp-$PRIVATE_NET_ID

# Ping first instance after status is active
sudo ip netns exec $NETNS_ID ping -c 3 10.0.0.3

# Log into first instance ( username is 'cirros', password is 'cubswin:)' )
sudo ip netns exec $NETNS_ID ssh cirros@10.0.0.3

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


MY_PUBLIC_SUBNET_CIDR=192.168.0.0/24
PUBLIC_NET_ID=`neutron net-create public --router:external=True | awk '/ id / { print $4 }'`
PUBLIC_SUBNET_ID=`neutron subnet-create --name public-subnet $PUBLIC_NET_ID $MY_PUBLIC_SUBNET_CIDR -- --enable_dhcp=False | awk '/ id / { print $4 ; }'`

neutron router-create real_router
neutron router-interface-add $real_router_id $priv_net_id
neutron router-gateway-set $real_router_id $pub_net_id
nova secgroup-add-rule default icmp -1 -1 0.0.0.0/0
nova secgroup-add-rule default tcp 22 22 0.0.0.0/0
nova list
nova boot --image cirros --flavor m1.tiny --nic net-id=$priv_net_id MySecondInstance

neutron port-list -f csv -c id -- --device_id=$instance_id | awk 'END{print};{gsub(/[\"\r]/,"")}'
neutron floatingip-create --port_id=$instance_port_id $pub_net_id


# http://docs.openstack.org/grizzly/openstack-compute/install/apt/content/cinder-install.html
dd if=/dev/zero of=cinder-volumes bs=1 count=0 seek=2G
losetup /dev/loop2 cinder-volumes
pvcreate /dev/loop2
vgcreate cinder-volumes /dev/loop2
pvscan

