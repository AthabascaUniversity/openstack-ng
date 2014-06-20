openstack-ng
============

Ansible playbook for setting up OpenStack infrastructure from scratch. Aims to replace openstack-setup and ansible-redhat-openstack

Assumptions
===========

1. Platform: RedHat
2. Distribution: RDO
3. Using OpenVSwitch & Neuron

Use
===

Setting up new platform
-----------------------

edit:
* hosts
* group_vars/

  * all.yml
  * neutron.yml
  * nova.yml
  * glance.yml
  * keystone.yml

Run::

  $ ansible-playbook -i hosts site.yml

Stop/start openstack services
-----------------------------

Stop::

  $ ansible-playbook -i hosts -t service_stop site.yml

Start::

  $ ansible-playbook -i hosts -t service_stop site.yml
