import  pulumi

from    sys         import path
from    os          import getenv
from    pulumi_aws  import efs

from    parse              import ParseYAML
from    aws.mandatory      import Mandatory
from    aws.subnet         import Subnets
from    aws.securitygroup  import SecurityGroups


# General variables
resource_type           = "efs"
resource_project        = getenv('IAC__PROJECT_ID')
resource_mandatory_tags = Mandatory.Tags()

# Resource dictionary
efs_ids_dict = {}

class EFS:

    def __init__(self):

        resource_specs  = ParseYAML(resource_type).getSpecs()
        aws_subnet_id   = Subnets.SubnetId()
        aws_sg_id       = SecurityGroups.SecurityGroupId()
        # aws_keypair_id  = KeyPairs.KeyPairId()

        for efs_name, efs_configuration in resource_specs.items():

            # Resource Name
            resource_name                           = efs_name

            # File System Configuration and its Default values
            resource_file_system                    = efs_configuration["file-system"]              if "file-system"        in efs_configuration        else None
            resource_file_system_encryption         = resource_file_system["encrypted"]             if "encrypted"          in resource_file_system     else True
            resource_file_system_performance_mode   = resource_file_system["performance_mode"]      if "performance_mode"   in resource_file_system     else "generalPurpose"

            # Target Configuration and its Default values
            resource_target                         = efs_configuration["target"]                   if "target"             in efs_configuration        else None
            resource_target_vpc                     = resource_target["vpc"]                        if "vpc"                in resource_target          else None
            resource_target_subnets                 = resource_target["subnets"]                    if "subnets"            in resource_target          else None
            resource_target_security_groups         = resource_target["security_groups"]            if "security_groups"    in resource_target          else None

            # Resource Tags and its Default values
            resource_tags                           = None
            resource_tags                           = efs_configuration["tags"]                     if "tags"               in efs_configuration        else None

            # Get the list of subnets from the configuration file
            # subnets_list = []
            # for each_subnet_found in resource_target_subnets:
            #     this_subnet = aws_subnet_id[str(each_subnet_found)]
            #     subnets_list.append(this_subnet)

            # Getting the list of security groups found
            security_groups_list = []
            for each_security_group_found in resource_target_security_groups:
                this_security_group = aws_sg_id[str(each_security_group_found)]
                security_groups_list.append(this_security_group)

            # Getting list of tags from configuration file
            tags_list                           = {}
            if resource_tags is not None:
                for each_tag_name, each_tag_value in resource_tags.items():
                    tags_list.update({each_tag_name: each_tag_value})

            # Adding mandatory tags
            tags_list.update({"Name": resource_name})
            tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
            tags_list.update(resource_mandatory_tags)

            #
            # Create EFS Resource
            #

            # EFS File System
            efs_file_system = efs.FileSystem(
                resource_name,
                encrypted           = resource_file_system_encryption,
                performance_mode    = resource_file_system_performance_mode,
                tags                = tags_list,
            )

            # Return a list of all EFSs created
            efs_ids_dict.update({efs_file_system._name: efs_file_system.id})

            # Create Target(s) based on the number of
            # Subnets found in the configuration file
            target_index = 0

            for each_subnet in resource_target_subnets:

                target_index = target_index + 1

                this_subnet = aws_subnet_id[str(each_subnet)]
                target_name = (resource_name+str("-target-" + str(target_index).zfill(2)))

                efs_target = efs.MountTarget(
                    target_name,
                    file_system_id          = efs_file_system.id,
                    subnet_id               = this_subnet,
                    security_groups         = security_groups_list
                )

    @staticmethod
    def EFSId():
        return efs_ids_dict
