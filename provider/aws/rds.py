#
# TODO:
# This module needs to be completed
#

import  pulumi
from    sys         import path
from    os          import getenv
from    pulumi_aws  import rds

# Custom modules
from parse              import ParseYAML
from aws.mandatory      import Mandatory
from aws.subnet         import Subnets
from aws.securitygroup  import SecurityGroups

# General variables
config                  = pulumi.Config()
resource_type           = "rds"
resource_project        = getenv('IAC__PROJECT_ID')
resource_mandatory_tags = Mandatory.Tags()

# Resource dictionaries
subnetgroup_ids_dict    = {}
parametergroup_ids_dict = {}

class RDS:

    @classmethod
    def Aurora(self):

        resource_specs          = ParseYAML(resource_type).getSpecs()
        aws_rds_subnet_group_id = RDS.SubnetGroupId()
        aws_sg_id               = SecurityGroups.SecurityGroupId()

        for rds_aurora_setup_type, rds_aurora_configuration in resource_specs["aurora"].items():

            # AWS RDS Aurora Dynamic Variables
            resource_setup_type             = rds_aurora_setup_type

            if resource_setup_type == "instance":

                for rds_instance_name, rds_instance_configuration in rds_aurora_configuration.items():

                    resource_instance_type          = rds_instance_configuration["instance_type"]
                    resource_engine                 = rds_instance_configuration["engine"]
                    resource_engine_version         = rds_instance_configuration["engine_version"]
                    resource_allocated_storage      = int(rds_instance_configuration["allocated_storage"])
                    # resource_storage_type           = rds_instance_configuration["storage_type"]
                    resource_subnet_group           = rds_instance_configuration["subnet_group"]
                    resource_parameter_group        = rds_instance_configuration["parameter_group"]
                    resource_security_groups        = rds_instance_configuration["security_groups"]
                    resource_database_name          = rds_instance_configuration["database_name"]
                    resource_username               = rds_instance_configuration["username"]
                    resource_password               = rds_instance_configuration["password"]
                    resource_security_groups_list   = []

                    this_subnet_group               = aws_rds_subnet_group_id[str(resource_subnet_group)]
                    # these_security_groups           = aws_sg_id[str(resource_security_groups)]

                    # Get the password from Pulumi Config
                    resource_retrieved_password = config.require_secret(resource_password)

                    for each_security_group_found in resource_security_groups:
                        resource_security_groups_list.append(aws_sg_id[str(each_security_group_found)])

                    aurora = rds.Instance(

                        rds_instance_name,
                        instance_class          = resource_instance_type,
                        engine                  = resource_engine,
                        engine_version          = resource_engine_version,
                        allocated_storage       = resource_allocated_storage,
                        # storage_type            = resource_storage_type,
                        db_subnet_group_name    = this_subnet_group,
                        parameter_group_name    = resource_parameter_group,
                        vpc_security_group_ids  = resource_security_groups_list,
                        name                    = resource_database_name,
                        username                = resource_username,
                        password                = resource_retrieved_password

                        )

                    pulumi.export(

                        aurora._name, [

                            aurora.address,
                            aurora.endpoint

                        ])

            # elif rds_aurora_configuration["setup_type"] == "cluster":

            #     print(rds_aurora_configuration["setup_type"])

            # else:

            #     print("Couldn't identify the setup type from your RDS YAML configration file")
            #     print("This should be being 'instance' or 'cluster'.")

        # default = rds.Cluster(
        #     "default",
        #     cluster_identifier="main-production-rds-aurora",
        #         availability_zones=[
        #             "eu-west-2a",
        #             "eu-west-2b",
        #             "eu-west-2c",
        #         ],
        #         database_name="mydb",
        #         master_username="foo",
        #         master_password="barbut8chars",
        #         final_snapshot_identifier = "lastsnapshot"
        # )

        # instances_count = range(0)
        # cluster_instances = []

        # for n in instances_count:

        #     cluster_instances.append(

        #         rds.ClusterInstance(

        #             f"clusterInstances-{n+1}",
        #             identifier=f"main-production-rds-aurora-{n+1}",
        #             cluster_identifier=default.id,
        #             instance_class="db.t3.medium",
        #             engine=default.engine,
        #             engine_version=default.engine_version,
        #             apply_immediately = True

        #         )

        #     )

    @classmethod
    def MySQL(self):
        pass

    @classmethod
    def MariaDB(self):
        pass

    @classmethod
    def PostgreSQL(self):
        pass

    @classmethod
    def Oracle(self):
        pass

    @classmethod
    def MicrosoftSQL(self):
        pass

    @classmethod
    def SubnetGroup(self):

        resource_specs  = ParseYAML(resource_type).getSpecs()
        aws_subnet_id   = Subnets.SubnetId()

        for subnetgroup_name, subnetgroup_configuration in resource_specs["subnet-group"].items():

            # AWS Elasticache Subnet Group Dynamic Variables
            resource_name           = subnetgroup_name
            resource_description    = subnetgroup_configuration["description"]
            resource_subnet_ids     = subnetgroup_configuration["subnets"]

            resource_tags           = None
            resource_tags           = subnetgroup_configuration["tags"] if "tags" in subnetgroup_configuration else None

            # Getting list of tags from configuration file
            tags_list               = {}
            if resource_tags is not None:
                for each_tag_name, each_tag_value in resource_tags.items():
                    tags_list.update({each_tag_name: each_tag_value})

            # Adding mandatory tags
            tags_list.update({"Name": resource_name})
            tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
            tags_list.update(resource_mandatory_tags)

            resource_subnets_list   = []

            for each_subnet_found in resource_subnet_ids:
                resource_subnets_list.append(aws_subnet_id[str(each_subnet_found)])

            subnetgroup         = rds.SubnetGroup(

                resource_name,
                description     = resource_description,
                subnet_ids      = resource_subnets_list,
                tags            = tags_list

            )

            # Update resource dictionary
            subnetgroup_ids_dict.update({subnetgroup._name: subnetgroup.id})

            # Export
            pulumi.export(subnetgroup._name, subnetgroup.id)

    @classmethod
    def SubnetGroupId(cls):

        return subnetgroup_ids_dict


    @classmethod
    def ParameterGroup(self):

        resource_specs  = ParseYAML(resource_type).getSpecs()
        aws_subnet_id   = Subnets.SubnetId()

        for parametergroup_name, parametergroup_configuration in resource_specs["parameter-group"].items():

            # AWS RDS Parameter Group Dynamic Variables
            resource_name           = parametergroup_name
            resource_description    = parametergroup_configuration["description"]
            resource_family         = parametergroup_configuration["family"]

            resource_tags           = None
            resource_tags           = parametergroup_configuration["tags"] if "tags" in parametergroup_configuration else None

            # Getting list of tags from configuration file
            tags_list               = {}
            if resource_tags is not None:
                for each_tag_name, each_tag_value in resource_tags.items():
                    tags_list.update({each_tag_name: each_tag_value})

            # Adding mandatory tags
            tags_list.update({"Name": resource_name})
            tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
            tags_list.update(resource_mandatory_tags)

            resource_subnets_list   = []

            # for each_subnet_found in resource_subnet_ids:
            #     resource_subnets_list.append(aws_subnet_id[str(each_subnet_found)])

            parametergroup      = rds.ParameterGroup(

                resource_name,
                name            = resource_name,
                description     = resource_description,
                family          = resource_family,
                tags            = tags_list

            )

            # Update resource dictionaries
            parametergroup_ids_dict.update({parametergroup._name: parametergroup.id})

            # Export
            pulumi.export(parametergroup._name, parametergroup.id)

    @classmethod
    def ParameterGroupId(cls):

        return parametergroup_ids_dict

    def OptionGroup(self):
        pass
