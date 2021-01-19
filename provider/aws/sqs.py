import  pulumi

from    os          import getenv
from    pulumi_aws  import sqs

# Custom packages
from parse          import ParseYAML
from aws.mandatory  import Mandatory

# General variables
resource_type           = "sqs"
resource_project        = getenv('IAC__PROJECT_ID')
resource_mandatory_tags = Mandatory.Tags()

class SQS:

    def __init__(self):

        resource_specs = ParseYAML(resource_type).getSpecs()

        for sqs_queue_name, sqs_queue_configuration in resource_specs.items():
            sqs_queue_configuration = sqs_queue_configuration if sqs_queue_configuration else {}

            resource_name           = sqs_queue_name

            resource_tags           = None
            resource_tags           = sqs_queue_configuration["tags"] if "tags" in sqs_queue_configuration else None

            # Getting list of tags from configuration file
            tags_list               = {}
            if resource_tags is not None:
                for each_tag_name, each_tag_value in resource_tags.items():
                    tags_list.update({each_tag_name: each_tag_value})

            # Adding mandatory tags
            tags_list.update({"Name": resource_name})
            tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
            tags_list.update(resource_mandatory_tags)

            fifo_queue = sqs_queue_configuration["fifo_queue"] if "fifo_queue" in sqs_queue_configuration else None
            content_based_deduplication = sqs_queue_configuration["content_based_deduplication"] if "content_based_deduplication" in sqs_queue_configuration else None
            delay_seconds = sqs_queue_configuration["delay_seconds"] if "delay_seconds" in sqs_queue_configuration else None
            max_message_size = sqs_queue_configuration["max_message_size_bytes"] if "max_message_size_bytes" in sqs_queue_configuration else None
            message_retention_seconds = sqs_queue_configuration["message_retention_seconds"] if "message_retention_seconds" in sqs_queue_configuration else None
            receive_wait_time_seconds = sqs_queue_configuration["receive_wait_time_seconds"] if "receive_wait_time_seconds" in sqs_queue_configuration else None
            visibility_timeout_seconds = sqs_queue_configuration["visibility_timeout_seconds"] if "visibility_timeout_seconds" in sqs_queue_configuration else None

            # Create SQSs
            queue              = sqs.Queue(
                resource_name,
                fifo_queue                  = fifo_queue,
                content_based_deduplication = content_based_deduplication,
                delay_seconds = delay_seconds,
                max_message_size = max_message_size,
                message_retention_seconds = message_retention_seconds,
                receive_wait_time_seconds = receive_wait_time_seconds,
                visibility_timeout_seconds = visibility_timeout_seconds,
                tags                        = tags_list
            )

            # Export
            pulumi.export(queue._name, queue.id)
