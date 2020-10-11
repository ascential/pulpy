import  pulumi
from    sys             import path
from    os              import getenv
from    pulumi_aws      import ec2 as igw

# Custom packages
from parse          import ParseYAML
from aws.mandatory  import Mandatory
from aws.vpc        import VPCs

# General variables
resource_type           = "internetgateway"
resource_project        = getenv('IAC__PROJECT_ID')
resource_mandatory_tags = Mandatory.Tags()

# Resource dictionaries
igw_ids_dict = {}

class InternetGateways:

    def __init__(self):

        resource_specs  = ParseYAML(resource_type).getSpecs()
        aws_vpc_id      = VPCs.VPCId()

        for igw_name, igw_configuration in resource_specs.items():

            # AWS Internet Gateway Variables
            resource_name   = igw_name
            resource_vpc    = igw_configuration["vpc"]

            resource_tags   = None
            resource_tags   = igw_configuration["tags"] if "tags" in igw_configuration else None

            this_vpc        = aws_vpc_id[str(resource_vpc)]

            # Getting list of tags from configuration file
            tags_list       = {}
            if resource_tags is not None:
                for each_tag_name, each_tag_value in resource_tags.items():
                    tags_list.update({each_tag_name: each_tag_value})

            # Adding mandatory tags
            tags_list.update({"Name": resource_name})
            tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
            tags_list.update(resource_mandatory_tags)

            aws_igw     = igw.InternetGateway(

                resource_name,
                vpc_id  = this_vpc,
                tags    = resource_tags

            )

            igw_ids_dict.update({aws_igw._name: aws_igw.id})

            # Export the name of each Internet Gateway
            pulumi.export(aws_igw._name, aws_igw.id)

    @classmethod
    def InternetGatewayId(cls):

        return igw_ids_dict