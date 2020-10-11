import  pulumi
from    sys         import path
from    os          import getenv
from    pulumi_aws  import ec2 as net

# Custom packages
from parse          import ParseYAML
from aws.mandatory  import Mandatory

# General variables
resource_type           = "vpc"
resource_project        = getenv('IAC__PROJECT_ID')
resource_mandatory_tags = Mandatory.Tags()

# Resource dictionaries
vpc_ids_dict = {}

class VPCs:

    def __init__(self):

        resource_specs = ParseYAML(resource_type).getSpecs()

        for vpc_name, vpc_conf in resource_specs.items():

            # AWS VPC Dynamic Variables
            resource_name           = vpc_name
            resource_cidr           = vpc_conf['cidr']
            resource_dns_resolution = vpc_conf['dns-resolution']
            resource_dns_hostnames  = vpc_conf['dns-hostnames']

            resource_tags           = None
            resource_tags           = vpc_conf["tags"] if "tags" in vpc_conf else None

            # Getting list of tags from configuration file
            tags_list               = {}
            if resource_tags is not None:
                for each_tag_name, each_tag_value in resource_tags.items():
                    tags_list.update({each_tag_name: each_tag_value})

            # Add mandatory tags
            tags_list.update({"Name": resource_name})
            tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
            tags_list.update(resource_mandatory_tags)

            # Create resource
            vpc = net.Vpc(

                resource_name,
                cidr_block              = resource_cidr,
                enable_dns_support      = resource_dns_resolution,
                enable_dns_hostnames    = resource_dns_hostnames,
                tags                    = tags_list

            )

            # Update resource dictionary
            vpc_ids_dict.update({vpc._name: vpc.id})

            # Export the name of each VPC
            pulumi.export(vpc._name, vpc.id)


    @classmethod
    def VPCId(cls):
        return vpc_ids_dict