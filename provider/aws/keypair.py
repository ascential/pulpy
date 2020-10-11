import  pulumi
from sys         import path
from os          import getenv
from pulumi_aws  import ec2 as am

# Custom packages
from parse          import ParseYAML
from aws.mandatory  import Mandatory

# General variables
resource_type           = "keypair"
resource_project        = getenv('IAC__PROJECT_ID')
resource_mandatory_tags = Mandatory.Tags()

# Resource dictionary
keypair_ids_dict = {}

class KeyPairs:

    def __init__(self):

        resource_specs  = ParseYAML(resource_type).getSpecs()

        for keypair_name, keypair_configuration in resource_specs.items():

            # AWS KeyPair Dynamic Variables
            resource_name       = keypair_name
            resource_public_key = keypair_configuration['public_key']

            resource_tags       = None
            resource_tags       = keypair_configuration["tags"] if "tags" in keypair_configuration else None

            # Getting list of tags from configuration file
            tags_list               = {}
            if resource_tags is not None:
                for each_tag_name, each_tag_value in resource_tags.items():
                    tags_list.update({each_tag_name: each_tag_value})

            # Adding mandatory tags
            tags_list.update({"Name": resource_name})
            tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
            tags_list.update(resource_mandatory_tags)

            # Create resource
            keypair                     = am.KeyPair(

                resource_name,
                public_key              = resource_public_key,
                tags                    = tags_list

            )

            # Update resource dictionary
            keypair_ids_dict.update({keypair._name: keypair.id})

            # Exporting each KeyPair ID created for future reference
            pulumi.export(keypair._name, keypair.id)

    @classmethod
    def KeyPairId(cls):

        return keypair_ids_dict