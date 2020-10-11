import  pulumi
from    sys         import path
from    os          import getenv
from    pulumi_aws  import ec2      as net

# Custom packages
from parse          import ParseYAML
from aws.mandatory  import Mandatory
from aws.subnet     import Subnets
from aws.elasticip  import ElasticIPs

# General variables
resource_type           = "natgateway"
resource_project        = getenv('IAC__PROJECT_ID')
resource_mandatory_tags = Mandatory.Tags()

# Resource dictionaries
natgw_ids_dict = {}

class NATGateways:

    def __init__(self):

        resource_specs  = ParseYAML(resource_type).getSpecs()
        aws_subnet_id   = Subnets.SubnetId()
        aws_eip_id      = ElasticIPs.ElasticIPId()

        for natgw_name, natgw_configuration in resource_specs.items():

            # AWS NAT Gateway Variables
            resource_name   = natgw_name
            resource_subnet = natgw_configuration["subnet"]
            resource_eip    = natgw_configuration["elastic_ip"]

            resource_tags   = None
            resource_tags   = natgw_configuration["tags"] if "tags" in natgw_configuration else None

            # Getting list of tags from configuration file
            tags_list               = {}
            if resource_tags is not None:
                for each_tag_name, each_tag_value in resource_tags.items():
                    tags_list.update({each_tag_name: each_tag_value})

            # Adding mandatory tags
            tags_list.update({"Name": resource_name})
            tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
            tags_list.update(resource_mandatory_tags)

            this_subnet     = aws_subnet_id[str(resource_subnet)]
            this_eip        = aws_eip_id[str(resource_eip)]

            aws_natgw       = net.NatGateway(

                resource_name,
                subnet_id       = this_subnet,
                allocation_id   = this_eip,
                tags            = tags_list

            )

            # Update resource dictionaries
            natgw_ids_dict.update({aws_natgw._name: aws_natgw.id})

            # Export
            pulumi.export(aws_natgw._name, aws_natgw.id)

    @classmethod
    def NATGatewayId(cls):

        return natgw_ids_dict