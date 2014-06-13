#!/bin/python

#>>> from keystoneclient.v2_0 import client
#>>> token = '012345SECRET99TOKEN012345'
#>>> endpoint = 'http://192.168.206.130:35357/v2.0'
#>>> keystone = client.Client(token=token, endpoint=endpoint)

#>>> from keystoneclient.v2_0 import client
#>>> username='adminUser'
#>>> password='secreetword'
#>>> tenant_name='openstackDemo'
#>>> auth_url='http://192.168.206.130:5000/v2.0'
#>>> keystone = client.Client(username=username, password=password,
#...                          tenant_name=tenant_name, auth_url=auth_url)

from keystoneclient.v2_0 import client,ec2
from lxml import etree
import sys
import argparse
import re

DEBUG=False

def debug(method):
    global DEBUG
    def new_method(*args,**kwargs):
        print method.__name__, args, kwargs
        return method(*args,**kwargs)
    if DEBUG:
    	return new_method
    else:
        return method

def logmethod(method):
    def new_method(self,*args,**kwargs):
        print method, args, kwargs,
        _method=getattr(self,'_H_%s' % method)
        res=_method(*args,**kwargs)
        print '-> ',res
        return res
    return new_method

class DebugMethods(type):
    def __new__(cls,classname,bases,classdict):
        logmatch = re.compile(classdict.get('logMatch','.*'))
        
        for attr,item in classdict.items():
            if callable(item) and logmatch.match(attr):
                classdict['_H_%s'%attr] = item    # rebind the method
                classdict[attr] = logmethod(attr) # replace method by wrapper

        return type.__new__(cls,classname,bases,classdict)


class KeystoneCore():
    __metaclass__=DebugMethods
    logMatch='.*'
    def __init__(self,god=True,**kwargs):
        if god:
            self.token=kwargs['token']
            self.endpoint=kwargs['endpoint']
            self.client = client.Client(token=self.token, endpoint=self.endpoint)
        else:
            self.username=kwargs['username']
            self.password=kwargs['password']
            self.tenant_name=kwargs['tenant']
            self.auth_url=kwargs['auth_url']

            self.client = client.Client(username=self.username, password=self.password,
                                     tenant_name=self.tenant_name, auth_url=self.auth_url)
            
    def role_create(self,name):
        r=self.client.roles.create(name)
        return r.id

    def tenant_create(self,name,description=""):
        t=self.client.tenants.create(tenant_name=name,description=description)
        return t.id

    def user_create(self,name,passwd,email,tenant_id=None):
        u=self.client.users.create(name=name,password=passwd,tenant_id=tenant_id,email=email)
        return u.id

    def user_role_add(self,user,role,tenant):
        self.client.roles.add_user_role(user,role,tenant)

    def service_create(self,name,stype,description):
        s=self.client.services.create(name,stype,description)
        return s.id

    def endpoint_create(self,region,service_id,public_url,admin_url,internal_url):
        e=self.client.endpoints.create(region=region,service_id=service_id,
                    publicurl=public_url,adminurl=admin_url,internalurl=internal_url)
        return e.id
    
    def ec2_credentials_create(self,user_id,tenant_id):
        return self.client.ec2.create(user_id,tenant_id)

    def ec2_credentials_list(self,user_id):
        return self.client.ec2.list(user_id)


class KeystoneDebug(KeystoneCore):
    def __init__(self,god=True,**kwargs):
        if god:
            self.token=kwargs['token']
            self.endpoint=kwargs['endpoint']
        else:
            self.username=kwargs['username']
            self.password=kwargs['password']
            self.tenant_name=kwargs['tenant']
            self.auth_url=kwargs['auth_url']

    def call(self,params):
        if self.token:
            # We're in God mode
            pre_str="keystone --token '%s' --endpoint '%s'" % (self.token,self.endpoint)
        else:
            # normal mode
            pre_str="keystone --os-username '%s' --os-password '%s' --os-tenant-name '%s' --os-auth-url '%s'" % \
                     ( self.username, self.password, self.tenant_name, self.auth_url )
                     
        print pre_str,params
   
    def role_create(self,name):
        self.call('role-create --name'+name)
        return name

    def tenant_create(self,name,description=""):
        self.call('tenant-create --name='+name+' --description="'+description+'"')
        return name

    def user_create(self,name,passwd,email,tenant_id=None):
        self.call('user-create --name="%s" --password="%s" --tenant-id="%s" --email="%s"' % \
                    (name,passwd,tenant_id,email))
        return name

    def user_role_add(self,user,role,tenant):
        self.call('add-user-role %s %s %s' % ( user, role, tenant ))
        # return ur

    def service_create(self,name,stype,description):
        self.call('service-create --name="%s" --type="%s" --description="%s"' % (name,stype,description))
        return name

    def endpoint_create(self,region,service_id,public_url,admin_url,internal_url):
        self.call('endpoint-create --region="%s" --service-id="%s" --adminurl="%s" --publicurl="%s" --internalurl="%s"' % \
                     (region,service_id,public_url,admin_url,internal_url))
        return region+service_id

    def ec2_credentials_create(self,user_id,tenant_id):
        class fake_EC2():
            user_id=None
            tenant_id=None
            access=None
            secret=None
        self.call('ec2-credentials-create --user-id="%s" --tenant-id="%s"' %(user_id,tenant_id))
        e=fake_EC2()
        e.user_id=user_id
        e.tenant_id=tenant_id
        e.access='access'+user_id+tenant_id
        e.secret='secret'+user_id+tenant_id
        return e

    def ec2_credentials_list(self,user_id):
        self.call('ec2-credentials-list --user-id="%s"' % (user_id))
        return ()


class KeystoneXMLSetup:
    id_hash=None
    def __init__(self,config,debug=True):
        self.id_hash={'user':{},'tenant':{},'role':{},'service':{},'endpoint':{}}
        if debug:
            Keystone=KeystoneDebug    
        else:
            Keystone=KeystoneCore
        self.ids={}
        self.ec2_tenant_users={}
        f=open(config,'r')
        self.config=etree.parse(f)
        f.close()
        env=self.config.xpath('/setup/env')[0]
        auth_nodes=env.xpath('auth')
        # print auth_nodes
        if auth_nodes:
            auth_node=auth_nodes[0]
        endpoint_nodes=env.xpath('endpoint')
        # print endpoint_nodes
        if endpoint_nodes:
            endpoint_node=endpoint_nodes[0]
        if endpoint_nodes:
            endpoint=endpoint_node.attrib['uri']
            token=endpoint_node.attrib['token']
            self.k=Keystone(god=True,endpoint=endpoint,token=token)
        elif auth_nodes:
            user=auth_node.attrib['user']
            password=auth_node.attrib['password']
            tenant=auth_node.attrib['tenant']
            auth_url=auth_node.attrib['uri']
            self.k=Keystone(god=False,user=user,password=password,tenant=tenant,auth_url=auth_url)
            
        ec2_nodes=env.xpath('ec2')
        self.ec2_admin_roles=[]
        if ec2_nodes:
            for e in ec2_nodes:
                self.ec2_admin_roles.append(e.attrib['admin_role'])
        else:
            self.ec2_admin_roles.append('admin')

        self.setupTenants()
        self.setupUsers()
        self.setupRoles()
        self.setupRoleMaps()
        self.setupServices()
        self.listEC2codes()

        # self.setupServices(enable_endpoints=True)
        #self.setupNova(enable_endpoints)
        #self.setupEC2(enable_endpoints)
        #self.setupGlance(enable_endpoints)
        #self.setupKeystone(enable_endpoints)
        #self.setupCinder(enable_endpoints)
        #self.setupHorizon(enable_endpoints)
        #if ENABLE_SWIFT: self.setupSwift(enable_endpoints)
        #if ENABLE_QUANTUM: self.setupQuantum(enable_endpoints)



    def setupTenants(self):
        self.ids['tenants']={}
        tenants=self.ids['tenants']

        tenant_elements=self.config.xpath('/setup/openstack/tenants/tenant')
        for te in tenant_elements:
            tenant_name=te.attrib['name']
            #tenant_ec2_user=te.attrib['ec2_user']
            tenants[tenant_name]=self.k.tenant_create(tenant_name)
            #self.ec2_tenant_users[tenant_ec2_user]=tenant_name

    def setupUsers(self):
        self.ids['users']={}
        tenants=self.ids['tenants']
        users=self.ids['users']

        user_elements=self.config.xpath('/setup/openstack/users/user')
        for ue in user_elements:
            user_name=ue.attrib['name']
            user_password=ue.attrib['password']
            user_email=ue.attrib['email']
            users[user_name]=self.k.user_create(user_name,user_password,user_email)
            #if self.ec2_tenant_users.has_key(user_name):
                #tenant_name=ec2_tenant_users[user_name]
                #my_ec2[(user_name,tenant_name)]=sef.k.ec2_credentials_create(users[user_name],tenants[tenant_name]))

    def setupRoles(self):
        self.ids['roles']={}
        roles=self.ids['roles']

        role_elements=self.config.xpath('/setup/openstack/roles/role')
        for re in role_elements:
            role_name=re.attrib['name']
            roles[role_name]=self.k.role_create(role_name)

    def setupRoleMaps(self):
        roles=self.ids['roles']
        users=self.ids['users']
        tenants=self.ids['tenants']
        self.ids['ec2']={}
        my_ec2=self.ids['ec2']

        rolemap_elements=self.config.xpath('/setup/openstack/rolemaps/rolemap')

        for rme in rolemap_elements:
            user=rme.attrib['user']
            role=rme.attrib['role']
            tenant=rme.attrib['tenant']
            self.k.user_role_add(users[user],   roles[role],    tenants[tenant])
            if role in self.ec2_admin_roles:
                my_ec2[(user,tenant)]=self.k.ec2_credentials_create(users[user],tenants[tenant])

    def setupServices(self,enable_endpoints=True):
        roles=self.ids['roles']
        users=self.ids['users']
        tenants=self.ids['tenants']
        
        self.ids['services']={}
        services=self.ids['services']
        
        services_elements=self.config.xpath('/setup/openstack/services')
        service_tenant_id=tenants[services_elements[0].attrib['tenant']]

        service_elements=self.config.xpath('/setup/openstack/services/service')
        
        service_elements.sort(lambda x,y : cmp(x.attrib['order'],y.attrib['order']))
        for se in service_elements:
            if se.attrib['disabled']=='True':
                continue
            sname=se.attrib['name']
            stype=se.attrib['type']
            sdesc=se.attrib['description']
            s=se.attrib['type']
            services[sname]=self.k.service_create(sname,stype,sdesc)
            regions=se.xpath('region')
            if regions:
                region=regions[0].attrib['name']
            else:
                region=None
            service_users=se.xpath('user')
            for u in service_users:
                uname=u.attrib['name']
                upassword=u.attrib['password']
                uemail=u.attrib['email']
                users[uname]=self.k.user_create(uname,upassword,uemail,service_tenant_id)
            if enable_endpoints:
                
                for addr in se.xpath('endpoint'):
                    admin_nodes=addr.xpath('address[@type="admin"]')
                    if admin_nodes:
                        admin_node=admin_nodes[0]
                    else: admin_node=None
                    public_nodes=addr.xpath('address[@type="public"]')
                    if public_nodes:
                        public_node=public_nodes[0]
                    else: public_node=None
                    internal_nodes=addr.xpath('address[@type="internal"]')
                    if internal_nodes:
                        internal_node=internal_nodes[0]
                    else: internal_node=None

                    ## print admin_node, public_node, internal_node
                    if admin_node is not None and public_node is not None and internal_node is not None:
                        ## if one of the addresses is undefined - can't proceed
                        self.k.endpoint_create(region,services[sname],
                            'http://'+public_node.attrib['host']+public_node.attrib['uri_suff'],
                            'http://'+admin_node.attrib['host']+admin_node.attrib['uri_suff'],
                            'http://'+internal_node.attrib['host']+internal_node.attrib['uri_suff']
                            )
                    else:
                        print "missing URLs", admin_nodes,public_nodes,internal_nodes
                            
    def listEC2codes(self):
        for (user,tenant) in self.ids['ec2']:
            print ">> ",user, tenant
            ec2_list=self.k.ec2_credentials_list(self.ids['users'][user])
            print ">>>> ",ec2_list
                
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Setup keystone sample data')
    parser.add_argument('data', type=str, nargs='?',
                     help='Keystone sample data in XML format')
    parser.add_argument('--dry-run', action='store_const', const=True, default=False,
                     help='Just pretend to execute',required=False)

    args=parser.parse_args(sys.argv[1:])
    KeystoneXMLSetup(args.data,args.dry_run)
    print "# Finished"
        
  
