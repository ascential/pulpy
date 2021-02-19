# SECTION EC2 Module

import base64
import pulumi

from sys                import path
from os                 import getenv
from base64             import b64encode
from pulumi_aws         import ec2, ebs, autoscaling

from parse              import ParseYAML
from aws.mandatory      import Mandatory
from aws.subnet         import Subnets
from aws.securitygroup  import SecurityGroups
from aws.keypair        import KeyPairs
# from aws.loadbalancer   import LoadBalancer

# General variables
resource_type           = "ec2"
resource_project        = getenv('IAC__PROJECT_ID')
resource_mandatory_tags = Mandatory.Tags()

# Resource dictionary
ec2_ids_dict    = {}
lt_ids_dict     = {}
asg_ids_dict    = {}

class EC2:


    # SECTION Instance
    # This method is used to create EC2 Instances

    @staticmethod
    def Instance():

        resource_specs  = ParseYAML(resource_type).getSpecs()
        aws_subnet_id   = Subnets.SubnetId()
        aws_sg_id       = SecurityGroups.SecurityGroupId()
        aws_keypair_id  = KeyPairs.KeyPairId()

        for ec2_instance_name, ec2_instance_configuration in resource_specs["instance"].items():

            # AWS EC2 Dynamic Variables
            resource_name                   = ec2_instance_name
            resource_number_of_instances    = ec2_instance_configuration["number_of_instances"]         if "number_of_instances"    in ec2_instance_configuration else 1
            resource_ami                    = ec2_instance_configuration["ami"]                         if "ami"                    in ec2_instance_configuration else None
            resource_instance_type          = ec2_instance_configuration["instance_type"]               if "instance_type"          in ec2_instance_configuration else None
            resource_subnet                 = ec2_instance_configuration["subnet"]                      if "subnet"                 in ec2_instance_configuration else None
            resource_security_groups        = ec2_instance_configuration["security_groups"]             if "security_groups"        in ec2_instance_configuration else None
            resource_ebs_optimization       = ec2_instance_configuration["ebs_optimization"]            if "ebs_optimization"       in ec2_instance_configuration else None
            resource_root_disk_volume_type  = ec2_instance_configuration["root_disk"]["volume_type"]    if "volume_type"            in ec2_instance_configuration["root_disk"] else None
            resource_root_disk_volume_size  = ec2_instance_configuration["root_disk"]["volume_size"]    if "volume_size"            in ec2_instance_configuration["root_disk"] else None
            resource_additional_disks       = ec2_instance_configuration["additional_disks"]            if "additional_disks"       in ec2_instance_configuration else None
            resource_public_ipv4_address    = ec2_instance_configuration["public_ipv4_address"]         if "public_ipv4_address"    in ec2_instance_configuration else None
            resource_keypair                = ec2_instance_configuration["ssh_key"]                     if "ssh_key"                in ec2_instance_configuration else None
            resource_user_data              = ec2_instance_configuration["user_data"]                   if "user_data"              in ec2_instance_configuration else None
            resource_password_data          = ec2_instance_configuration["password"]                    if "password"               in ec2_instance_configuration else None

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
            if resource_keypair is not None:
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
                    ebs_optimized               = resource_ebs_optimization,
                    root_block_device           = {
                        "volume_type" : resource_root_disk_volume_type,
                        "volume_size" : resource_root_disk_volume_size
                    },
                    user_data                   = resource_user_data,
                    get_password_data           = resource_password_data,
                    tags                        = tags_list

                )

                #
                # Additional Disks (EBS Volumes)
                #

                if resource_additional_disks is not None:

                    # This variable is used down below
                    # by Volume Attachment
                    additional_disks_found = 0

                    for additional_disk_name, additional_disk_config in resource_additional_disks.items():

                        if additional_disk_name is not None:

                            # Setting up the default values
                            # for each individual EBS volume
                            default_additional_disk_config_az   = ec2_instance.availability_zone
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
                            size                = additional_disk_config_size,

                            tags                = {
                                "Name": additional_disk_name,
                            }

                        )

                        #
                        # EBS Volume Attachment
                        #

                        additional_disks_letter         = range(98, 123) # Getting a letter between 'b' and 'z'
                        additional_disk_assigned_letter = additional_disks_letter[additional_disks_found]
                        additional_disk_device_lettet   = "/dev/sd{:c}".format(additional_disk_assigned_letter)

                        ebs_attachment = ec2.VolumeAttachment(

                            (additional_disk_name + "-attachment"),
                            device_name = additional_disk_device_lettet,
                            volume_id   = ebs_volume.id,
                            instance_id = ec2_instance.id

                        )

                        additional_disks_found = additional_disks_found + 1

                # NOTE EC2 ID Dictionary
                # Update resource dictionaries
                ec2_ids_dict.update({ec2_instance._name: ec2_instance.id})

                # NOTE Values Test
                # Print statements below are used only for
                # testing the functionality, can be ignored
                # print("Instance name:", ec2_instance._name)
                # print("Instance ID:", ec2_instance.id)

                # Export the name of each EC2 Instance
                pulumi.export(ec2_instance._name,
                    [
                        {
                            "ID"                    : ec2_instance.id,
                            "ARN"                   : ec2_instance.arn,
                            "State"                 : ec2_instance.instance_state,
                            "Password (Windows)"    : ec2_instance.password_data,
                            "Private DNS"           : ec2_instance.private_dns,
                            "Public DNS"            : ec2_instance.public_dns,
                            "Public IP"             : ec2_instance.public_ip,
                            "Primary ENI"           : ec2_instance.primary_network_interface_id
                        }
                    ]
                )

        # NOTE Dictionary Test
        # Print statements below are used only for
        # testing the functionality, can be ignored
        # print("Dictionary:", ec2_ids_dict)
    # !SECTION

    # SECTION Instance IDs

    # Return gathered dictionaries
    @staticmethod
    def EC2Id():
        return ec2_ids_dict

    # !SECTION

    # SECTION Auto Scaling Group
    @staticmethod
    def AutoScalingGroup():

        resource_specs          = ParseYAML(resource_type).getSpecs()
        aws_subnet_id           = Subnets.SubnetId()
        aws_launch_template_id  = EC2.LTId()
        # aws_target_group_arn    = LoadBalancer.TargetGroupArn()

        # Cheking if "auto-scaling-group:" is present in the configuration file
        autoscaling_group = resource_specs["auto-scaling-group"].items() if "auto-scaling-group" in resource_specs else None

        # If "auto-scaling-group:" is present then we'll run all the code below
        if autoscaling_group is not None:

            for autoscaling_group_name, autoscaling_group_configuration in autoscaling_group:

                # AWS Autoscaling Group Dynamic Variables

                # Resource Name
                resource_name               = autoscaling_group_name

                # Autoscaling Group Configuration and its Default values
                resource_min_size           = autoscaling_group_configuration["min-size"]           if "min-size"           in autoscaling_group_configuration  else 1
                resource_max_size           = autoscaling_group_configuration["max-size"]           if "max-size"           in autoscaling_group_configuration  else 1
                resource_desired_capacity   = autoscaling_group_configuration["desired-capacity"]   if "desired-capacity"   in autoscaling_group_configuration  else 1
                resource_subnets            = autoscaling_group_configuration["subnets"]            if "subnets"            in autoscaling_group_configuration  else None
                resource_capacity_rebalance = autoscaling_group_configuration["capacity-rebalance"] if "capacity-rebalance" in autoscaling_group_configuration  else False
                resource_cooldown_period    = autoscaling_group_configuration["cooldown-period"]    if "cooldown-period"    in autoscaling_group_configuration  else 300
                resource_health_check_type  = autoscaling_group_configuration["health-check-type"]  if "health-check-type"  in autoscaling_group_configuration  else None
                resource_launch_template    = autoscaling_group_configuration["launch-template"]    if "launch-template"    in autoscaling_group_configuration  else None
                resource_target_groups      = autoscaling_group_configuration["target-groups"]      if "target-groups"      in autoscaling_group_configuration  else None

                # Resource Tags and its Default values
                resource_tags               = None
                resource_tags               = autoscaling_group_configuration["tags"]               if "tags"               in autoscaling_group_configuration  else None

                # Getting list of tags from configuration file
                tags_list               = {}
                if resource_tags is not None:
                    for each_tag_name, each_tag_value in resource_tags.items():
                        tags_list.update({each_tag_name: each_tag_value})

                # Adding mandatory tags
                tags_list.update({"Name": resource_name})
                tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
                tags_list.update(resource_mandatory_tags)

                # List of all Subnets gathered from "subnets:" key
                resource_subnets_list = []

                for each_subnet_found in resource_subnets:
                    individual_subnet_id = aws_subnet_id[str(each_subnet_found)]
                    resource_subnets_list.append(individual_subnet_id)


                # Check if "launch-template" is provided or not
                if resource_launch_template is not None:
                    this_launch_template_id = aws_launch_template_id[str(resource_launch_template)]

                # FIXME It complains about circular import
                # Check if "target-groups:" is provided or not
                # resource_target_group_arns = []

                # if resource_target_groups is not None:
                #     individual_tg_arn = aws_target_group_arn[str(resource_target_groups)]
                #     resource_target_group_arns.append(individual_tg_arn)


                # Create the Autoscaling Group
                autoscaling_group = autoscaling.Group(

                    autoscaling_group_name,
                    # name                    = autoscaling_group_name,
                    min_size                = resource_min_size,
                    max_size                = resource_max_size,
                    desired_capacity        = resource_desired_capacity,
                    vpc_zone_identifiers    = resource_subnets_list,
                    capacity_rebalance      = resource_capacity_rebalance,
                    default_cooldown        = resource_cooldown_period,
                    health_check_type       = resource_health_check_type,
                    launch_template         = {
                        "id": this_launch_template_id,
                        },
                    # NOT available using this module version
                    instance_refresh        = {
                        "strategy": "Rolling",
                        "triggers": "launch_template"
                        },
                    # tags                = tags_list,
                    # target_group_arns       = resource_target_group_arns

                )

                # NOTE Auto Scaling Group ID Dictionary
                # Update resource dictionaries
                asg_ids_dict.update({autoscaling_group._name: autoscaling_group.id})

    # !SECTION

    # SECTION Auto Scaling Group IDs
    # Return gathered dictionaries
    @staticmethod
    def ASGId():

        return asg_ids_dict
    # !SECTION

    # SECTION Launch Template

    @staticmethod
    def LaunchTemplate():

        resource_specs  = ParseYAML(resource_type).getSpecs()
        aws_sg_id       = SecurityGroups.SecurityGroupId()
        aws_keypair_id  = KeyPairs.KeyPairId()

        # Cheking if "auto-scaling-group:" is present in the configuration file
        launch_template = resource_specs["launch-template"].items() if "launch-template" in resource_specs else None

        # If "auto-scaling-group:" is present then we'll run all the code below
        if launch_template is not None:

            # Loop through all Launch Templates defined
            for launch_template_name, launch_template_configuration in launch_template:

                # If there's any configuration then we'll execute the
                # code below, else we'll pass the execution
                if launch_template_configuration is not None:

                    # AWS Launch Template Dynamic Variables

                    # Resource Name
                    resource_name                   = launch_template_name

                    # AWS Launch Template configuration and its Default values
                    resource_description            = launch_template_configuration["description"]              if "description"            in launch_template_configuration else None
                    resource_instance_type          = launch_template_configuration["instance-type"]            if "instance-type"          in launch_template_configuration else None
                    resource_ami                    = launch_template_configuration["ami"]                      if "ami"                    in launch_template_configuration else None
                    resource_key                    = launch_template_configuration["key"]                      if "key"                    in launch_template_configuration else None
                    resource_ebs_optimized          = launch_template_configuration["ebs-optimized"]            if "ebs-optimized"          in launch_template_configuration else True
                    resource_termination_protection = launch_template_configuration["termination-protection"]   if "termination-protection" in launch_template_configuration else False
                    resource_security_groups        = launch_template_configuration["security-groups"]          if "security-groups"        in launch_template_configuration else None
                    resource_user_data              = launch_template_configuration["user-data"]                if "user-data"              in launch_template_configuration else None
                    resource_update_default_version = launch_template_configuration["update-default-version"]   if "update-default-version" in launch_template_configuration else True

                    # Resource Tags and its Default values
                    resource_tags                   = None
                    resource_tags                   = launch_template_configuration["tags"]                     if "tags"                   in launch_template_configuration else None

                    # Getting list of tags from configuration file
                    tags_list = {}
                    if resource_tags is not None:
                        for each_tag_name, each_tag_value in resource_tags.items():
                            tags_list.update({each_tag_name: each_tag_value})

                    # Adding mandatory tags
                    tags_list.update({"Name": resource_name})
                    tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
                    tags_list.update(resource_mandatory_tags)

                    # Check if the KeyPair is provided or not
                    if resource_key is None:
                        this_keypair = None
                    else:
                        this_keypair = aws_keypair_id[str(resource_key)]

                    # Getting the list of security groups found
                    security_groups_list = []
                    for each_security_group_found in resource_security_groups:
                        this_security_group = aws_sg_id[str(each_security_group_found)]
                        security_groups_list.append(this_security_group)

                    # user_data_bytes   = resource_user_data.encode("utf-8")
                    # user_data_base64  = b64encode(user_data_bytes)

                    new_launch_template = ec2.LaunchTemplate(

                        resource_name,
                        description             = resource_description,
                        instance_type           = resource_instance_type,
                        image_id                = resource_ami,
                        key_name                = this_keypair,
                        ebs_optimized           = resource_ebs_optimized,
                        disable_api_termination = resource_termination_protection,
                        vpc_security_group_ids  = security_groups_list,
                        # It has to be base64 encoded
                        # user_data               = b64encode(user_data_bytes),
                        tags                    = tags_list,
                        update_default_version  = resource_update_default_version

                    )

                    # NOTE Launch Templates ID Dictionary
                    # Update resource dictionaries
                    lt_ids_dict.update({new_launch_template._name: new_launch_template.id})

    # !SECTION

    # SECTION Launch Template IDs
    # Return gathered dictionaries
    @staticmethod
    def LTId():

        return lt_ids_dict
    # !SECTION

# !SECTION
