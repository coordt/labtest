===========================
Specifying Backing Services
===========================

Backing services are external services your project needs in order to work properly, such as a database, a cache, or a search index.

Pre-existing Services
=====================

You can manually set up shared backing services in your laboratory environment. To use these services in your experiments, you simply have to provide the appropriate environment variables in the configuration. For example, if you are sharing a Memcached server, you might add:

.. code-block:: yaml
    :caption: Specifying shared services in the configuration

    labtest:
      environment:
        - MEMCACHE_URL=10.20.4.121:11211

Then your project can use the environment variable ``MEMCACHE_URL`` to configure itself in the experiment.


On-Demand Services
==================

You can also have LabTest manage your backing services for each experiment. LabTest will provision the service and set environment variables in your experiment's container.

On-demand services are specified in the ``services`` section of the experiment configuration. Each service will require at least two parameters: *provider* and *provision type.*

Providers
---------

A provider is the method of hosting the backing service you need. Right now only AWS is supported, but others will be possible in the future.


.. _backing_services_provision_types:

Provision types
---------------

LabTest supports three types of provisioning of backing services: *communal,* *independent,* and *shared.*

In a *communal* server provisioning, only one server is running, but each experiment might have their own independent part of it, depending on the service type. For example, in a communal database service, there is one server instance, but LabTest will manage an exclusive database on that server for each experiment. LabTest will provision the server instance, if it doesn't exist, and will never destroy it. Individual databases are created and destroyed with the experiements.

In an *independent* server provisioning, each experiment has their own service instance. LabTest creates and destroys the server instance with the experiment.

In a *shared* server provisioning, an experiment uses the exact service instance as another experiment. No provisioning is done at all. You will also have to specify the ``shared_instance_name`` so LabTest can retrieve the appropriate configuration information.


On-Demand service types
=======================

Databases: MySQL and PostgreSQL
-------------------------------

MySQL and PostgreSQL services are defined in the same way:

.. code-block:: yaml
    :caption: Specifying a MySQL database backing service in the configuration

    labtest:
      services:
        mysql:
          provider: aws
          provision_type: independent
          initial_data_source: /mnt/backups/myapp-backups/myapp.bak.gz
          data_setup_script: /mnt/backups/myapp-backups/myapp-restore.sh

.. code-block:: yaml
    :caption: Specifying a PostgreSQL database backing service in the configuration

    labtest:
      services:
        postgresql:
          provider: aws
          provision_type: independent
          initial_data_source: /mnt/backups/myapp-backups/myapp.bak.gz
          data_setup_script: /mnt/backups/myapp-backups/myapp-restore.sh

You can initialize the databases with two parameters: ``initial_data_source`` and ``data_setup_script``\ . If you don't need to initialize the database, you can leave these out.

LabTest makes these environment variables available to your Docker container:

- ``DATABASE_URL``\ : The URL to the database server
- ``DATABASE_NAME``\ : The name of the database on the server
- ``DATABASE_USERNAME``\ : The username to access the database
- ``DATABASE_PASSWORD``\ : The password for the corresponding username


provider
~~~~~~~~

*Default:* ``aws``
*Acceptable values: ``aws``

Currently only ``aws`` is supported.

provision_type
~~~~~~~~~~~~~~

*Default:* ``communal``
*Acceptable values:* ``communal``\ , ``independent``\ , ``shared``

See :ref:`backing_services_provision_types` for more information about each type. If the provision type is ``shared``\ , you also need to specify the ``shared_instance_name``\ .

shared_instance_name
~~~~~~~~~~~~~~~~~~~~

*Default:* ``None``
*Acceptable values:* Name of another experiment

This parameter is only required if you specify ``provision_type: shared``\ . The value is the name of the experiment responsible for the database.

shared_app_name
~~~~~~~~~~~~~~~

*Default:* The current ``app_name`` for this project
*Acceptable values:* Name of another application (another ``app_name``\ )

You only need to specify this parameter if you need to share a database with another application for some reason. You need to set the ``shared_instance_name`` as well.

initial_data_source
~~~~~~~~~~~~~~~~~~~

*Default:* ``None``
*Acceptable values:* Directory or path

The ``initial_data_source`` parameter is optional. It can work independently or synergistically with the ``data_setup_script`` parameter.

This parameter uses the default database restoration tool for the database type to restore a file to the database. If the value is a directory, LabTest retrieves the most recent file in that directory. If the value is a file, LabTest uses the indicated file.

If the ``data_setup_script`` is specified, this process will occur before that script is called.

data_setup_script
~~~~~~~~~~~~~~~~~

*Default:* ``None``
*Acceptable values:* Full or relative path

This optional parameter allows you to use a script to do whatever extra steps necessary to get the database ready.

If the value is a relative path, LabTest assumes it is relative to the root of the code repository.





Steps: Shared DB Server
-----------------------



DB server provision types:
For shared servers, we need to have a standard name that we can use for discovery via the API to get the DB info.

1. Look for existing communal database server. (default is 'communal')

   ``aws rds describe-db-instances --db-instance-identifier communal``

3. Look for existing ClientSecurityGroup (from https://github.com/widdix/aws-cf-templates/blob/master/state/client-sg.yaml)

This client security group is used to limit from where the database accepts connections. Only resources in this security group can connect.

5. Look for existing DatabaseSecurityGroup.

   ``aws rds describe-db-security-groups --db-security-group-name communal``

6. Look for existing DBSubnetGroup.

8. Create server

What LabTest will provide during provisioning:

DBName (if necessary)
MasterUserPassword


  ClientSecurityGroup:
    Type: 'AWS::EC2::SecurityGroup'
    Properties:
      GroupDescription: !Ref 'AWS::StackName'
      VpcId:
        'Fn::ImportValue': !Sub '${ParentVPCStack}-VPC'



  DatabaseSecurityGroup:
    Type: 'AWS::EC2::SecurityGroup'
    Properties:
      GroupDescription: !Ref 'AWS::StackName'
      VpcId:
        'Fn::ImportValue': !Sub '${ParentVPCStack}-VPC'
      SecurityGroupIngress:
      - IpProtocol: tcp
        FromPort: 5432
        ToPort: 5432
        SourceSecurityGroupId:
          'Fn::ImportValue': !Sub '${ParentClientStack}-ClientSecurityGroup'


  DBSubnetGroup:
    Type: 'AWS::RDS::DBSubnetGroup'
    Properties:
      DBSubnetGroupDescription: !Ref 'AWS::StackName'
      SubnetIds: !Split
      - ','
      - 'Fn::ImportValue':
          !Sub '${ParentVPCStack}-SubnetsPrivate'




  DBInstance:
    Type: 'AWS::RDS::DBInstance'
    Properties:
      AllocatedStorage: !If [HasDBSnapshotIdentifier, !Ref 'AWS::NoValue', !Ref DBAllocatedStorage]
      AllowMajorVersionUpgrade: false
      AutoMinorVersionUpgrade: true
      BackupRetentionPeriod: !Ref DBBackupRetentionPeriod
      CopyTagsToSnapshot: true
      DBInstanceClass: !Ref DBInstanceClass
      DBName: !Ref DBName
      DBSnapshotIdentifier: !If [HasDBSnapshotIdentifier, !Ref DBSnapshotIdentifier, !Ref 'AWS::NoValue']
      DBSubnetGroupName: !Ref DBSubnetGroup
      Engine: postgres
      EngineVersion: '9.6.5'
      KmsKeyId: !If [HasEncryption, !Ref Key, !Ref 'AWS::NoValue']
      MasterUsername: !If [HasDBSnapshotIdentifier, !Ref 'AWS::NoValue', !Ref DBMasterUsername]
      MasterUserPassword: !If [HasDBSnapshotIdentifier, !Ref 'AWS::NoValue', !Ref DBMasterUserPassword]
      MultiAZ: !Ref DBMultiAZ
      PreferredBackupWindow: '09:54-10:24'
      PreferredMaintenanceWindow: 'sat:07:00-sat:07:30'
      StorageType: gp2
      StorageEncrypted: !If [HasDBSnapshotIdentifier, !Ref 'AWS::NoValue', !Ref Encryption]
      VPCSecurityGroups:
      - !Ref DatabaseSecurityGroup
