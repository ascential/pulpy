from arpeggio import Empty
import  pulumi
from    sys             import path
from    os              import getenv
from    pulumi_aws      import ec2      as net

# Custom packages
from parse          import ParseYAML
from aws.mandatory  import Mandatory

# General variables
resource_type           = "elasticip"
resource_project        = getenv('IAC__PROJECT_ID')
resource_mandatory_tags = Mandatory.Tags()

# Resource dictionaries
eip_ids_dict = {}

class ElasticIPs:

    def __init__(self):

        resource_specs  = ParseYAML(resource_type).getSpecs()

        for eip_name, eip_configuration in resource_specs.items():

            # AWS Elastic IP Dynamic Variables
            resource_name   = eip_name
            resource_tags   = eip_configuration["tags"] if "'tags':" in str(eip_configuration) else None

            # Lists
            tags_list       = {}

            # Getting list of tags from configuration file
            if resource_tags is not None:
                for each_tag_name, each_tag_value in resource_tags.items():
                    tags_list.update({each_tag_name: each_tag_value})

            # Adding mandatory tags
            tags_list.update({"Name": resource_name})
            tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
            tags_list.update(resource_mandatory_tags)

            eip             = net.Eip(

                resource_name,
                tags = tags_list

            )

            eip_ids_dict.update({eip._name: eip.id})

            # Exporting each EIP
            pulumi.export(eip._name, eip.id)

    @classmethod
    def ElasticIPId(cls):
        return eip_ids_dict