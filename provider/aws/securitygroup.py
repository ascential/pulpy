import  pulumi
from    sys         import path
from    os          import getenv
from    pulumi_aws  import ec2      as net

# Custom packages
from parse          import ParseYAML
from aws.mandatory  import Mandatory
from aws.vpc        import VPCs

# General variables
resource_type           = "securitygroup"
resource_project        = getenv('IAC__PROJECT_ID')
resource_mandatory_tags = Mandatory.Tags()

# Resource dictionary
sg_ids_dict = {}

class SecurityGroups:

    def __init__(self):

        resource_specs  = ParseYAML(resource_type).getSpecs()
        aws_vpc_id      = VPCs.VPCId()

        for sg_name, sg_configuration in resource_specs.items():

            # AWS Security Groups Dynamic Variables
            resource_name           = sg_name
            resource_description    = sg_configuration["description"]
            resource_vpc            = sg_configuration["vpc"]
            resource_ingress_rules  = sg_configuration["ingress"]
            resource_egress_rules   = sg_configuration["egress"]

            resource_tags           = None
            resource_tags           = sg_configuration["tags"] if "tags" in sg_configuration else None

            # Getting list of tags from configuration file
            tags_list               = {}
            if resource_tags is not None:
                for each_tag_name, each_tag_value in resource_tags.items():
                    tags_list.update({each_tag_name: each_tag_value})

            # Adding mandatory tags
            tags_list.update({"Name": resource_name})
            tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
            tags_list.update(resource_mandatory_tags)

            this_vpc                = aws_vpc_id[str(resource_vpc)]

            # Empty dictionaries that'll be populated with rules
            # coming from each individual security group,
            # being ingress or egress
            ingress_rules_list      = {}
            egress_rules_list       = {}

            # Gathering all ingress rules and return the results
            # to the right dictionary defined above
            for each_ingress_rule in resource_ingress_rules.items():
                for each_ingress_rule_key, each_ingress_rule_value in [each_ingress_rule]:
                    ingress_rules_list.update({each_ingress_rule_key: each_ingress_rule_value})
            combined_ingress_rules  = list(ingress_rules_list.values())

            # Gathering all egress rules and return the results
            # to the right dictionary defined above
            for each_egress_rule in resource_egress_rules.items():
                for each_egress_rule_key, each_egress_rule_value in [each_egress_rule]:
                    egress_rules_list.update({each_egress_rule_key: each_egress_rule_value})
            combined_egress_rules   = list(egress_rules_list.values())

            # Create Security Group
            security_group      = net.SecurityGroup(

                resource_name,
                description     = resource_description,
                name            = resource_name,
                vpc_id          = this_vpc,
                ingress         = combined_ingress_rules,
                egress          = combined_egress_rules,
                tags            = tags_list

            )

            # Update resource dictionary
            sg_ids_dict.update({security_group._name: security_group.id})

            # Exporting each security group created for future reference
            pulumi.export(security_group._name, security_group.id)

    @classmethod
    def SecurityGroupId(cls):

        return sg_ids_dict