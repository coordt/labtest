===================
Amazon Web Services
===================

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


.. code-block:: yaml

    ClientSecurityGroup:
      Type: 'AWS::EC2::SecurityGroup'
      Properties:
        GroupDescription: !Ref 'AWS::StackName'
        VpcId:
          'Fn::ImportValue': !Sub '${ParentVPCStack}-VPC'


.. code-block:: yaml

    PostgresDatabaseSecurityGroup:
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


.. code-block:: yaml

    DBSubnetGroup:
      Type: 'AWS::RDS::DBSubnetGroup'
      Properties:
        DBSubnetGroupDescription: !Ref 'AWS::StackName'
        SubnetIds: !Split
        - ','
        - 'Fn::ImportValue':
            !Sub '${ParentVPCStack}-SubnetsPrivate'


.. code-block:: yaml

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
