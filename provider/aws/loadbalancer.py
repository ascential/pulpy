import  pulumi
from    sys         import path
from    os          import getenv
from    pulumi_aws  import lb

# Custom packages
from parse              import ParseYAML
from aws.mandatory      import Mandatory
from aws.vpc            import VPCs
from aws.subnet         import Subnets
from aws.securitygroup  import SecurityGroups
from aws.ec2            import EC2

# General variables
resource_type           = "loadbalancer"
resource_project        = getenv('IAC__PROJECT_ID')
resource_mandatory_tags = Mandatory.Tags()

# Resource dictionaries

target_group_ids_dict   = {}

class LoadBalancer:

#
# Application Load Balancer
#

    def ALB(self):

        resource_specs  = ParseYAML(resource_type).getSpecs()
        aws_subnet_id   = Subnets.SubnetId()
        aws_sg_id       = SecurityGroups.SecurityGroupId()

        for alb_name, alb_configuration in resource_specs["alb"].items():

            # AWS ALB Dynamic Variables
            resource_specific_type          = "alb"
            resource_name                   = alb_name
            resource_subnets                = alb_configuration["subnets"]              if "subnets"                in alb_configuration else None
            resource_security_groups        = alb_configuration["security_groups"]      if "security_groups"        in alb_configuration else None
            resource_deletion_protection    = alb_configuration["deletion_protection"]  if "deletion_protection"    in alb_configuration else None
            resource_exposure               = alb_configuration["exposure"]             if "exposure"               in alb_configuration else None
            resource_http2                  = alb_configuration["http2"]                if "http2"                  in alb_configuration else None
            resource_idle_timeout           = alb_configuration["idle_timeout"]         if "idle_timeout"           in alb_configuration else None
            resource_listeners              = alb_configuration["listeners"]            if "listeners"              in alb_configuration else None

            resource_tags                   = None
            resource_tags                   = alb_configuration["tags"] if "tags" in alb_configuration else None

            # Getting list of tags from configuration file
            tags_list = {}
            if resource_tags is not None:
                for each_tag_name, each_tag_value in resource_tags.items():
                    tags_list.update({each_tag_name: each_tag_value})

            # Adding mandatory tags
            tags_list.update({"Name": resource_name})
            tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
            tags_list.update(resource_mandatory_tags)

            resource_subnets_list = []
            for each_subnet_found in resource_subnets:
                resource_subnets_list.append(aws_subnet_id[str(each_subnet_found)])

            resource_security_groups_list = []
            for each_security_group_found in resource_security_groups:
                resource_security_groups_list.append(aws_sg_id[str(each_security_group_found)])

            # ALB exposure [internal|external]
            # - internal for private connections (VPN, TGW etc.)
            # - external for internet-facing / publicly exposed load balancers
            if resource_exposure is not None:
                if resource_exposure == "internal":
                    resource_exposure is False
                elif resource_exposure == "external":
                    resource_exposure is True
                else:
                    resource_exposure = None


            # NOTE: Work in progress

            # Listeners [http|https]
            # if resource_listeners is not None:
            #     # print("Found listeners")
            #     for listener_protocol in resource_listeners.items():
            #         print(listener_protocol)
            #         if listener_protocol[0] == "http":
            #             print("HTTP Found")
            #         elif listener_protocol[0] == "https":
            #             print("HTTPS Found")
            #         else:
            #             print("No valid ALB listener found, must be 'http' or 'https'")


            # FIXME:
            # This needs to be reviewed as currently the subnets
            # are being added in a non-dynamic fashion
            alb = lb.LoadBalancer(

                resource_name,
                load_balancer_type  = "application",
                name                = resource_name,

                subnet_mappings=[
                    lb.LoadBalancerSubnetMappingArgs(
                        subnet_id       = resource_subnets_list[0],
                    ),
                    lb.LoadBalancerSubnetMappingArgs(
                        subnet_id       = resource_subnets_list[1],
                    ),
                    lb.LoadBalancerSubnetMappingArgs(
                        subnet_id       = resource_subnets_list[2],
                    ),
                ],

                security_groups     = resource_security_groups_list,
                enable_deletion_protection = resource_deletion_protection,
                internal            = bool(resource_exposure),
                enable_http2        = resource_http2,
                idle_timeout        = resource_idle_timeout,
                tags                = tags_list

                )

#
# Classic Load Balancer
#

    @classmethod
    def CLB(self):
        pass


#
# Network Load Balancer
#

    @classmethod
    def NLB(self):
        pass


#
# Target Group
#

    @classmethod
    def TargetGroup(self):

        resource_specs  = ParseYAML(resource_type).getSpecs()
        aws_vpc_id      = VPCs.VPCId()
        aws_ec2_id      = EC2.EC2Id()

        for target_group_name, target_group_configuration in resource_specs["targetgroup"].items():

            # AWS Target Group Dynamic Variables
            resource_name       = target_group_name
            resource_port       = target_group_configuration["port"]
            resource_protocol   = target_group_configuration["protocol"]
            resource_vpc        = target_group_configuration["vpc"]

            resource_tags       = None
            resource_tags       = target_group_configuration["tags"] if "tags" in target_group_configuration else None

            # Getting list of tags from configuration file
            tags_list = {}
            if resource_tags is not None:
                for each_tag_name, each_tag_value in resource_tags.items():
                    tags_list.update({each_tag_name: each_tag_value})

            # Adding mandatory tags
            tags_list.update({"Name": resource_name})
            tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
            tags_list.update(resource_mandatory_tags)


            this_vpc                        = aws_vpc_id[str(resource_vpc)]

            # Create Instance Target Group
            target_group                    = lb.TargetGroup(

                resource_name,
                name        = resource_name,
                port        = resource_port,
                protocol    = resource_protocol,
                vpc_id      = this_vpc,
                tags        = tags_list

            )

            target_group_ids_dict.update({target_group._name: target_group.id})

            # Export the name of each Instance Target Group
            pulumi.export(resource_name, target_group.id)

            # Target Group Attachments / Targets
            target_group_attachment_index = 0
            for each_tg_instance in target_group_configuration["instances"]:

                target_group_attachment_index = target_group_attachment_index + 1

                this_ec2                = aws_ec2_id[str(each_tg_instance)]

                target_group_attachment = lb.TargetGroupAttachment(

                    (resource_name + "-at-" + str(target_group_attachment_index)),
                    target_group_arn    = target_group.arn,
                    target_id           = this_ec2,
                    port                = resource_port

                )


    #
    # Target Group ID
    #

    @classmethod
    def TargetGroupId(cls):

        return target_group_ids_dict
