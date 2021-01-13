import  pulumi
from    sys         import path
from    os          import getenv
from    pulumi_aws  import docdb

# Custom packages
from parse              import ParseYAML
from aws.mandatory      import Mandatory
from aws.subnet         import Subnets
from aws.securitygroup  import SecurityGroups

# General variables
config                  = pulumi.Config()
resource_type           = "documentdb"
resource_project        = getenv('IAC__PROJECT_ID')
resource_mandatory_tags = Mandatory.Tags()

# Resource dictionaries
subnetgroup_ids_dict    = {}
parametergroup_ids_dict = {}

class DocumentDB:

    @classmethod
    def Cluster(self):

        resource_specs          = ParseYAML(resource_type).getSpecs()
        aws_docdb_sng_id        = DocumentDB.SubnetGroupId()
        aws_docdb_pg_id         = DocumentDB.ParameterGroupId()
        aws_sg_id               = SecurityGroups.SecurityGroupId()

        for docdb_name, docdb_configuration in resource_specs["cluster"].items():

            # AWS DocumentDB Dynamic Variables
            resource_name                           = (docdb_name + "-cluster")
            resource_identifier                     = (docdb_name + "-cluster")
            resource_engine                         = docdb_configuration["engine"]
            resource_engine_version                 = docdb_configuration["engine_version"]
            resource_az                             = docdb_configuration["az"]
            resource_subnet_group                   = docdb_configuration["subnet_group"]
            resource_parameter_group                = docdb_configuration["parameter_group"]
            resource_security_groups                = docdb_configuration["security_groups"]
            resource_port                           = docdb_configuration["port"]
            resource_master_username                = docdb_configuration["master_username"]
            resource_master_password                = docdb_configuration["master_password"]
            resource_backup_retention_period        = docdb_configuration["backup_retention_period"]
            resource_preferred_backup_window        = docdb_configuration["preferred_backup_window"]
            resource_preferred_maintenance_window   = docdb_configuration["preferred_maintenance_window"]
            resource_deletion_protection            = docdb_configuration["deletion_protection"]
            resource_apply_immediately              = docdb_configuration["apply_immediately"]
            resource_skip_final_snapshot            = docdb_configuration["skip_final_snapshot"]

            resource_tags                           = None
            resource_tags                           = docdb_configuration["tags"] if "tags" in docdb_configuration else None

            this_subnet_group                       = aws_docdb_sng_id[str(resource_subnet_group)]
            this_parameter_group                    = aws_docdb_pg_id[str(resource_parameter_group)]

            security_groups_list                    = []

            # Get the password from Pulumi Config
            resource_retrieved_password = config.require_secret(resource_master_password)

            # Getting list of tags from configuration file
            tags_list = {}
            if resource_tags is not None:
                for each_tag_name, each_tag_value in resource_tags.items():
                    tags_list.update({each_tag_name: each_tag_value})

            # Adding mandatory tags
            tags_list.update({"Name": resource_name})
            tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
            tags_list.update(resource_mandatory_tags)

            for each_security_group_found in resource_security_groups:

                this_security_group = aws_sg_id[str(each_security_group_found)]
                security_groups_list.append(this_security_group)

            documentdb = docdb.Cluster(

                resource_name,
                cluster_identifier              = resource_identifier,
                engine                          = resource_engine,
                engine_version                  = resource_engine_version,
                availability_zones              = resource_az,
                db_subnet_group_name            = this_subnet_group,
                db_cluster_parameter_group_name = this_parameter_group,
                vpc_security_group_ids          = security_groups_list,
                port                            = resource_port,
                master_username                 = resource_master_username,
                master_password                 = resource_retrieved_password,
                backup_retention_period         = resource_backup_retention_period,
                preferred_backup_window         = resource_preferred_backup_window,
                preferred_maintenance_window    = resource_preferred_maintenance_window,
                deletion_protection             = resource_deletion_protection,
                skip_final_snapshot             = resource_skip_final_snapshot,
                apply_immediately               = resource_apply_immediately,
                tags                            = tags_list

            )

            for number_of_instances in range (1, int(docdb_configuration["instances"]["number_of_instances"])+1):

                resource_instance_name          = (docdb_name + "-instance" + str("-" + str(number_of_instances)).zfill(4))
                resource_instance_class         = docdb_configuration["instances"]["instance_class"]

                cluster_instance = docdb.ClusterInstance(

                    resource_instance_name,
                    identifier          = resource_instance_name,
                    cluster_identifier  = documentdb.id,
                    instance_class      = resource_instance_class

                )

            pulumi.export(documentdb._name, [("Cluster ID:", documentdb.id), ("Cluster Endpoint:", documentdb.endpoint)])


    @classmethod
    def SubnetGroup(self):

        resource_specs  = ParseYAML(resource_type).getSpecs()
        aws_subnet_id   = Subnets.SubnetId()

        for subnetgroup_name, subnetgroup_configuration in resource_specs["subnet-group"].items():

            # AWS DocumentDB Subnet Group Dynamic Variables
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

            subnetgroup                 = docdb.SubnetGroup(

                resource_name,
                description             = resource_description,
                subnet_ids              = resource_subnets_list,
                tags                    = tags_list

            )

            # Update resource dictionaries
            subnetgroup_ids_dict.update({subnetgroup._name: subnetgroup.id})

            # Export
            pulumi.export(subnetgroup._name, subnetgroup.id)

    @classmethod
    def SubnetGroupId(cls):

        return subnetgroup_ids_dict

    @classmethod
    def ParameterGroup(self):

        resource_specs  = ParseYAML(resource_type).getSpecs()

        for parametergroup_name, parametergroup_configuration in resource_specs["parameter-group"].items():

            # AWS DocumentDB Parameter Group Dynamic Variables
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

            # Add mandatory tags
            tags_list.update({"Name": resource_name})
            tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
            tags_list.update(resource_mandatory_tags)

            # Getting all parameters for each
            # individual DocumentDB Parameter Group
            resource_parameters     = []

            for each_parameter_key, each_parameter_value in parametergroup_configuration["parameters"].items():

                resource_parameters.append({"name": each_parameter_key, "value": each_parameter_value["value"], "applyMethod": each_parameter_value["apply"]},)

            # Create resource
            parametergroup          = docdb.ClusterParameterGroup(

                resource_name,
                name                = resource_name,
                description         = resource_description,
                family              = resource_family,
                parameters          = resource_parameters,
                tags                = tags_list

            )

            # Update resource dictionary
            parametergroup_ids_dict.update({parametergroup._name: parametergroup.id})

            # Export parameter group
            pulumi.export(parametergroup._name, parametergroup.id)


    @classmethod
    def ParameterGroupId(cls):

        return parametergroup_ids_dict