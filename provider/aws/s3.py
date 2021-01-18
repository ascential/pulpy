import  pulumi
from    sys         import path
from    os          import getenv
from    pulumi_aws  import s3

# Custom packages
from parse          import ParseYAML
from aws.mandatory  import Mandatory

# General variables
resource_type           = "s3"
resource_project        = getenv('IAC__PROJECT_ID')
resource_mandatory_tags = Mandatory.Tags()

class S3:

    def __init__(self):

        resource_specs = ParseYAML(resource_type).getSpecs()

        for s3_bucket_name, s3_bucket_configuration in resource_specs.items():

            # AWS S3 Dynamic Variables
            resource_name           = s3_bucket_name

            resource_tags           = None
            resource_tags           = s3_bucket_configuration["tags"] if "tags" in s3_bucket_configuration else None

            # Getting list of tags from configuration file
            tags_list               = {}
            if resource_tags is not None:
                for each_tag_name, each_tag_value in resource_tags.items():
                    tags_list.update({each_tag_name: each_tag_value})

            # Adding mandatory tags
            tags_list.update({"Name": resource_name})
            tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
            tags_list.update(resource_mandatory_tags)

            sse_config = s3_bucket_configuration["serverSideEncryptionConfiguration"] if "serverSideEncryptionConfiguration" in s3_bucket_configuration else None

            # Create S3s
            bucket              = s3.Bucket(

                resource_name,
                acl             = s3_bucket_configuration["acl"],
                force_destroy   = s3_bucket_configuration["force-destroy"],
                tags            = tags_list
                server_side_encryption_configuration = sse_config
            )

            # Export
            pulumi.export(bucket._name, bucket.id)