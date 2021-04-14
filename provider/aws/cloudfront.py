import  pulumi

from    os          import getenv
from    pulumi_aws  import cloudfront

# Custom packages
from parse          import ParseYAML
from aws.mandatory  import Mandatory

# General variables
resource_type           = "cloudfront"
resource_project        = getenv('IAC__PROJECT_ID')
resource_mandatory_tags = Mandatory.Tags()

class CloudFront:

    def __init__(self):

        resource_specs = ParseYAML(resource_type).getSpecs()

        for cloudfront_distribution_name, cloudfront_distribution_configuration in resource_specs.items():
            cloudfront_distribution_configuration = cloudfront_distribution_configuration if cloudfront_distribution_configuration else {}

            resource_name           = cloudfront_distribution_name

            resource_tags           = None
            resource_tags           = cloudfront_distribution_name["tags"] if "tags" in cloudfront_distribution_name else None

            # Getting list of tags from configuration file
            tags_list               = {}
            if resource_tags is not None:
                for each_tag_name, each_tag_value in resource_tags.items():
                    tags_list.update({each_tag_name: each_tag_value})

            # Adding mandatory tags
            tags_list.update({"Name": resource_name})
            tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
            tags_list.update(resource_mandatory_tags)

            aliases                 = cloudfront_distribution_configuration["aliases"]                  if "aliases"                    in cloudfront_distribution_configuration else None
            default_cache_behavior  = cloudfront_distribution_configuration["default_cache_behavior"]   if "default_cache_behavior"     in cloudfront_distribution_configuration else None
            enabled                 = cloudfront_distribution_configuration["enabled"]                  if "enabled"                    in cloudfront_distribution_configuration else None
            ordered_cache_behaviors = cloudfront_distribution_configuration["ordered_cache_behaviors"]  if "ordered_cache_behaviors"    in cloudfront_distribution_configuration else None
            origins                 = cloudfront_distribution_configuration["origins"]                  if "origins"                    in cloudfront_distribution_configuration else None
            price_class             = cloudfront_distribution_configuration["price_class"]              if "price_class"                in cloudfront_distribution_configuration else None
            viewer_certificate      = cloudfront_distribution_configuration["viewer_certificate"]       if "viewer_certificate"         in cloudfront_distribution_configuration else None
            custom_error_responses  = cloudfront_distribution_configuration["custom_error_responses"]   if "custom_error_responses"     in cloudfront_distribution_configuration else None
            restrictions            = cloudfront_distribution_configuration["restrictions"]             if "restrictions"               in cloudfront_distribution_configuration else { "geoRestriction": { "restrictionType": "none" } }

            # Create Cloudfront Distribution
            distribution = cloudfront.Distribution(
                resource_name,
                aliases                 = aliases,
                default_cache_behavior  = default_cache_behavior,
                enabled                 = enabled,
                ordered_cache_behaviors = ordered_cache_behaviors,
                origins                 = origins,
                price_class             = price_class,
                viewer_certificate      = viewer_certificate,
                tags                    = tags_list,
                restrictions            = restrictions,
                default_root_object     = "index.html",
                custom_error_responses  = custom_error_responses,
                is_ipv6_enabled         = True
            )

            # Export
            pulumi.export(distribution._name, distribution.id)
