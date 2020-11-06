import  pulumi, yaml

from    sys         import path
from    os          import getenv
from    pulumi_aws  import ec2, ebs

from parse              import ParseYAML
from aws.mandatory      import Mandatory
from aws.subnet         import Subnets
from aws.securitygroup  import SecurityGroups
from aws.keypair        import KeyPairs

# General variables
resource_type           = "ec2"
resource_project        = getenv('IAC__PROJECT_ID')
resource_mandatory_tags = Mandatory.Tags()

# Resource dictionary
ec2_ids_dict = {}

class EC2:

    def __init__(self):

        resource_specs  = ParseYAML(resource_type).getSpecs()
        aws_subnet_id   = Subnets.SubnetId()
        aws_subnet_az   = Subnets.SubnetAZ()
        aws_sg_id       = SecurityGroups.SecurityGroupId()
        aws_keypair_id  = KeyPairs.KeyPairId()

        for ec2_instance_name, ec2_instance_configuration in resource_specs.items():

            # AWS EC2 Dynamic Variables
            resource_name                   = ec2_instance_name
            resource_number_of_instances    = ec2_instance_configuration["number_of_instances"]         if "number_of_instances"    in ec2_instance_configuration else None
            resource_ami                    = ec2_instance_configuration["ami"]                         if "ami"                    in ec2_instance_configuration else None
            resource_instance_type          = ec2_instance_configuration["instance_type"]               if "instance_type"          in ec2_instance_configuration else None
            resource_subnet                 = ec2_instance_configuration["subnet"]                      if "subnet"                 in ec2_instance_configuration else None
            resource_security_groups        = ec2_instance_configuration["security_groups"]             if "security_groups"        in ec2_instance_configuration else None
            resource_root_disk_volume_type  = ec2_instance_configuration["root_disk"]["volume_type"]    if "volume_type"            in ec2_instance_configuration["root_disk"] else None
            resource_root_disk_volume_size  = ec2_instance_configuration["root_disk"]["volume_size"]    if "volume_size"            in ec2_instance_configuration["root_disk"] else None
            resource_additional_disks       = ec2_instance_configuration["additional_disks"]            if "additional_disks"       in ec2_instance_configuration else None
            resource_public_ipv4_address    = ec2_instance_configuration["public_ipv4_address"]         if "public_ipv4_address"    in ec2_instance_configuration else None
            resource_keypair                = ec2_instance_configuration["ssh_key"]                     if "ssh_key"                in ec2_instance_configuration else None
            resource_user_data              = ec2_instance_configuration["user_data"]                   if "user_data"              in ec2_instance_configuration else None

            resource_tags                   = None
            resource_tags                   = ec2_instance_configuration["tags"] if "tags" in ec2_instance_configuration else None

            # Getting list of tags from configuration file
            tags_list                       = {}
            if resource_tags is not None:
                for each_tag_name, each_tag_value in resource_tags.items():
                    tags_list.update({each_tag_name: each_tag_value})

            # Adding mandatory tags
            tags_list.update({"Name": resource_name})
            tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
            tags_list.update(resource_mandatory_tags)

            this_subnet = aws_subnet_id[str(resource_subnet)]

            # Check if the KeyPair is provided or not
            if resource_keypair is None:
                this_keypair = None
            else:
                this_keypair = aws_keypair_id[str(resource_keypair)]

            # Getting the list of security groups found
            security_groups_list = []
            for each_security_group_found in resource_security_groups:
                this_security_group = aws_sg_id[str(each_security_group_found)]
                security_groups_list.append(this_security_group)

            for number_of_instances in range (1, int(resource_number_of_instances)+1):

                if resource_number_of_instances > 1:
                    resource_final_name = (resource_name+str("-" + str(number_of_instances)).zfill(4))
                else:
                    resource_final_name = resource_name

                #
                # Create EC2
                #

                ec2_instance                    = ec2.Instance(

                    resource_final_name,
                    ami                         = resource_ami,
                    instance_type               = resource_instance_type,
                    associate_public_ip_address = resource_public_ipv4_address,
                    subnet_id                   = this_subnet,
                    vpc_security_group_ids      = security_groups_list,
                    key_name                    = this_keypair,
                    root_block_device           = {
                        "volume_type" : resource_root_disk_volume_type,
                        "volume_size" : resource_root_disk_volume_size
                    },
                    user_data                   = resource_user_data,
                    tags                        = tags_list

                )

                #
                # Additional Disks (EBS Volumes)
                #

                if resource_additional_disks is not None:

                    for additional_disk_name, additional_disk_config in resource_additional_disks.items():

                        if additional_disk_name is not None:

                            # Getting the EC2 Subnet AZ, this will be used
                            # as the default in case none is provided
                            ec2_subnet_az = aws_subnet_az[str(resource_subnet)]

                            # Setting up the default values
                            # for each individual EBS volume
                            default_additional_disk_config_az   = ec2_subnet_az
                            default_additional_disk_config_type = "gp2"
                            default_additional_disk_config_size = 20

                            if additional_disk_config is not None:

                                additional_disk_config_az   = additional_disk_config["availability_zone"]   if "availability_zone"  in additional_disk_config else default_additional_disk_config_az
                                additional_disk_config_type = additional_disk_config["volume_type"]         if "volume_type"        in additional_disk_config else default_additional_disk_config_type
                                additional_disk_config_size = additional_disk_config["volume_size"]         if "volume_size"        in additional_disk_config else default_additional_disk_config_size

                            else:

                                additional_disk_config_az   = default_additional_disk_config_az
                                additional_disk_config_type = default_additional_disk_config_type
                                additional_disk_config_size = default_additional_disk_config_size

                        # Create EBS Volume
                        ebs_volume = ebs.Volume(
                            additional_disk_name,
                            availability_zone   = additional_disk_config_az,
                            type                = additional_disk_config_type,
                            size                = additional_disk_config_size
                        )

                # Update resource dictionaries
                ec2_ids_dict.update({ec2_instance._name: ec2_instance.id})

                # Export the name of each EC2 Instance
                pulumi.export(ec2_instance._name, ec2_instance.id)

    @classmethod
    def EC2Id(cls):

        return ec2_ids_dict
