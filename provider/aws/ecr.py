import  pulumi
from    sys        import path
from    os         import getenv
from    pulumi_aws import eks

# Custom packages
from parse              import ParseYAML
from aws.mandatory      import Mandatory

# General variables
resource_type           = "ecr"
resource_project        = getenv('IAC__PROJECT_ID')
resource_mandatory_tags = Mandatory.Tags()

class ECR:

    def __init__(self):

        resource_specs      = ParseYAML(resource_type).getSpecs()

        #
        # ECR Repository
        #

        for ecr_repo_name, ecr_repo_configuration in resource_specs.items():

            # AWS ECR Dynamic Variables
            resource_repo_name          = ecr_repo_name
            # resource_repo_version      = eks_repo_configuration["version"]

            resource_repo_tags          = None
            resource_repo_tags          = ecr_repo_configuration["tags"] if "tags" in ecr_repo_configuration else None

            # Getting list of tags from configuration file
            repo_tags_list                           = {}

            if resource_repo_tags is not None:
                for each_tag_name, each_tag_value in resource_repo_tags.items():
                    repo_tags_list.update({each_tag_name: each_tag_value})

            # Adding mandatory tags
            repo_tags_list.update({"Name": resource_repo_name})
            repo_tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
            repo_tags_list.update(resource_mandatory_tags)