import  pulumi

from    os          import getenv
from    pulumi_aws  import lambda_

# Custom packages
from parse          import ParseYAML
from aws.mandatory  import Mandatory
from aws.iam        import IAM
from aws.sqs        import SQS

# General variables
resource_type           = "lambda"
resource_project        = getenv('IAC__PROJECT_ID')
resource_mandatory_tags = Mandatory.Tags()

lambdas_by_name = {}

class Lambda:

    def __init__(self):

        resource_specs = ParseYAML(resource_type).getSpecs()

        for lambda_name, config in resource_specs.items():
            config = config if config else {}

            resource_name           = lambda_name
            resource_tags           = config.get("tags")

            # Getting list of tags from configuration file
            tags_list               = {}
            if resource_tags is not None:
                for each_tag_name, each_tag_value in resource_tags.items():
                    tags_list.update({each_tag_name: each_tag_value})

            # Adding mandatory tags
            tags_list.update({"Name": resource_name})
            tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
            tags_list.update(resource_mandatory_tags)

            lambda_function = lambda_.Function(
                lambda_name,
                handler                             = config.get("handler"),
                code                                = pulumi.AssetArchive({ ".": pulumi.FileAsset("./hello_world.jar") }),
                memory_size                         = config.get("memory_size"),
                name                                = lambda_name,
                publish                             = config.get("publish"),
                reserved_concurrent_executions      = config.get("reserved_concurrent_executions"),
                role                                = IAM.RoleARN()[config.get("role")],
                runtime                             = config.get("runtime"),
                timeout                             = config.get("timeout")
            )

            # Export
            pulumi.export(lambda_function._name, lambda_function.id)

            # Event source mappings
            for mapping_name, mapping_config in config.get("event_source_mapping").items():

                event_source = mapping_config["event_source"]
                assert event_source.get("type") == "sqs", "Just sqs is currently supported as event source mapping. You're welcome to implement more."

                source_arn = SQS.ByName()[event_source["name"]].arn

                mapping = lambda_.EventSourceMapping(
                    mapping_name,
                    event_source_arn                = source_arn,
                    function_name                   = lambda_function.arn,
                    batch_size                      = mapping_config.get("batch_size")
                )
                pulumi.export(mapping_name, mapping)


            lambdas_by_name[lambda_name] = lambda_function

    @classmethod
    def ByName(cls):
        return lambdas_by_name
