import  pulumi
from    sys         import path
from    os          import getenv
from    pulumi_aws  import ec2 as net

# Custom packages
from parse          import ParseYAML
from aws.mandatory  import Mandatory
from aws.vpc        import VPCs

# General variables
resource_type           = "subnet"
resource_project        = getenv('IAC__PROJECT_ID')
resource_mandatory_tags = Mandatory.Tags()

# Resource dictionaries
subnet_ids_dict         = {}
subnetscidrblocks_dict  = {}

class Subnets:

    def __init__(self):

        resource_specs  = ParseYAML(resource_type).getSpecs()
        aws_vpc_id      = VPCs.VPCId()

        for subnet_name, subnet_configuration in resource_specs.items():

            # AWS Subnet Dynamic Variables
            resource_name               = subnet_name
            resource_az                 = subnet_configuration["az"]
            resource_cidr               = subnet_configuration["cidr"]
            resource_assign_public_ipv4 = subnet_configuration["assign-public-ipv4"]
            resource_vpc                = subnet_configuration["vpc"]

            resource_tags               = None
            resource_tags               = subnet_configuration["tags"] if "'tags':" in str(subnet_configuration) else None

            this_vpc                    = aws_vpc_id[str(resource_vpc)]

            # Getting list of tags from configuration file
            tags_list                   = {}
            if resource_tags is not None:
                for each_tag_name, each_tag_value in resource_tags.items():
                    tags_list.update({each_tag_name: each_tag_value})

            # Adding mandatory tags
            tags_list.update({"Name": resource_name})
            tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
            tags_list.update(resource_mandatory_tags)

            subnet      = net.Subnet(

                resource_name,
                vpc_id                      = this_vpc,
                cidr_block                  = resource_cidr,
                map_public_ip_on_launch     = resource_assign_public_ipv4,
                availability_zone           = resource_az,
                tags                        = tags_list

                # FIXME: This needs to be sorted
                # opts = pulumi.ResourceOptions(
                #     parent      = this_vpc,
                #     depends_on  = [this_vpc]
                # )

            )

            subnet_ids_dict.update({subnet._name: subnet.id})
            subnetscidrblocks_dict.update({subnet._name: subnet.cidr_block})

            # Exporting each subnet created for future reference
            pulumi.export(subnet._name, subnet.id)

    @classmethod
    def SubnetId(cls):
        return subnet_ids_dict

    @classmethod
    def getSubnetCidrBlock(cls):
        return subnetscidrblocks_dict