import  pulumi
from    sys         import path
from    os          import getenv
from    pulumi_aws  import elasticache

# Custom packages
from parse              import ParseYAML
from aws.mandatory      import Mandatory
from aws.subnet         import Subnets
from aws.securitygroup  import SecurityGroups

# General variables
resource_type           = "elasticache"
resource_project        = getenv('IAC__PROJECT_ID')
resource_mandatory_tags = Mandatory.Tags()

# Resource dictionaries
subnetgroup_ids_dict    = {}

# Possible name clash
class Elasticache:

    def Redis(self):

        resource_specs                  = ParseYAML(resource_type).getSpecs()
        aws_elasticache_subnet_group_id = Elasticache.SubnetGroupId()
        aws_sg_id                       = SecurityGroups.SecurityGroupId()

        for elasticache_redis_name, elasticache_redis_configuration in resource_specs["redis"].items():

            # AWS EC2 Dynamic Variables
            resource_specific_type          = "redis"
            resource_name                   = elasticache_redis_name
            resource_number_of_nodes        = elasticache_redis_configuration["number_of_nodes"]
            resource_node_type              = elasticache_redis_configuration["node_type"]
            resource_engine_version         = elasticache_redis_configuration["engine_version"]
            resource_port                   = elasticache_redis_configuration["port"]
            resource_subnet_group           = elasticache_redis_configuration["subnet_group"]
            resource_parameter_group        = elasticache_redis_configuration["parameter_group"]
            resource_security_groups        = elasticache_redis_configuration["security_groups"]

            resource_tags                   = None
            resource_tags                   = elasticache_redis_configuration["tags"] if "tags" in elasticache_redis_configuration else None

            # Getting list of tags from configuration file
            tags_list                       = {}
            if resource_tags is not None:
                for each_tag_name, each_tag_value in resource_tags.items():
                    tags_list.update({each_tag_name: each_tag_value})

            # Adding mandatory tags
            tags_list.update({"Name": resource_name})
            tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
            tags_list.update(resource_mandatory_tags)

            resource_security_groups_list   = []

            this_subnet_group               = aws_elasticache_subnet_group_id[str(resource_subnet_group)]

            for each_security_group_found in resource_security_groups:
                resource_security_groups_list.append(aws_sg_id[str(each_security_group_found)])
            # this_security_group         = aws_sg_id[str(resource_security_groups)]

            redis = elasticache.Cluster(

                resource_name,
                engine                  = resource_specific_type,
                num_cache_nodes         = resource_number_of_nodes,
                node_type               = resource_node_type,
                engine_version          = resource_engine_version,
                port                    = resource_port,
                subnet_group_name       = this_subnet_group,
                parameter_group_name    = resource_parameter_group,
                security_group_ids      = resource_security_groups_list,
                tags                    = tags_list

                )

    def SubnetGroup(self):

        resource_specs  = ParseYAML(resource_type).getSpecs()
        aws_subnet_id   = Subnets.SubnetId()

        for subnetgroup_name, subnetgroup_configuration in resource_specs["subnet-group"].items():

            # AWS Elasticache Subnet Group Dynamic Variables
            resource_name           = subnetgroup_name
            resource_description    = subnetgroup_configuration["description"]
            resource_subnet_ids     = subnetgroup_configuration["subnets"]
            resource_subnets_list   = []

            for each_subnet_found in resource_subnet_ids:
                resource_subnets_list.append(aws_subnet_id[str(each_subnet_found)])

            subnetgroup                 = elasticache.SubnetGroup(

                resource_name,
                description             = resource_description,
                subnet_ids              = resource_subnets_list

            )

            subnetgroup_ids_dict.update({subnetgroup._name: subnetgroup.id})

            # Exporting each Elasticache Subnet Group created for future reference
            pulumi.export(subnetgroup._name, subnetgroup.id)

    @classmethod
    def SubnetGroupId(cls):

        return subnetgroup_ids_dict