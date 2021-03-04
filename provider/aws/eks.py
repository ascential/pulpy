import  pulumi
from    sys        import path
from    os         import getenv
from    pulumi_aws import eks

# Custom packages
from parse              import ParseYAML
from aws.mandatory      import Mandatory
from aws.subnet         import Subnets
from aws.iam            import IAM
from aws.securitygroup  import SecurityGroups

# General variables
resource_type           = "eks"
resource_project        = getenv('IAC__PROJECT_ID')
resource_mandatory_tags = Mandatory.Tags()

class EKS:

    @staticmethod
    def Cluster():

        resource_specs      = ParseYAML(resource_type).getSpecs()
        aws_subnet_id       = Subnets.SubnetId()
        aws_iam_role_arn    = IAM.RoleARN()
        aws_sgs_ids         = SecurityGroups.SecurityGroupId()

        #
        # EKS Cluster
        #

        for eks_cluster_name, eks_cluster_configuration in resource_specs["cluster"].items():

            # AWS EKS Cluster Dynamic Variables
            resource_cluster_name                       = eks_cluster_name
            resource_cluster_version                    = eks_cluster_configuration["version"]                  if "version"                    in eks_cluster_configuration else None
            resource_cluster_role_arn                   = eks_cluster_configuration["role"]                     if "role"                       in eks_cluster_configuration else None
            resource_cluster_subnets                    = eks_cluster_configuration["subnets"]                  if "subnets"                    in eks_cluster_configuration else None
            resource_cluster_security_groups            = eks_cluster_configuration["security_groups"]          if "security_groups"            in eks_cluster_configuration else None
            resource_cluster_endpoint_private_access    = eks_cluster_configuration["endpoint_private_access"]  if "endpoint_private_access"    in eks_cluster_configuration else None
            resource_cluster_endpoint_public_access     = eks_cluster_configuration["endpoint_public_access"]   if "endpoint_public_access"     in eks_cluster_configuration else None
            resource_cluster_public_access_cidrs        = eks_cluster_configuration["public_access_cidrs"]      if "public_access_cidrs"        in eks_cluster_configuration else None

            resource_cluster_tags                       = None
            resource_cluster_tags                       = eks_cluster_configuration["tags"] if "tags" in eks_cluster_configuration else None

            # Getting list of tags from configuration file
            cluster_tags_list                           = {}
            if resource_cluster_tags is not None:
                for each_tag_name, each_tag_value in resource_cluster_tags.items():
                    cluster_tags_list.update({each_tag_name: each_tag_value})

            # Adding mandatory tags
            cluster_tags_list.update({"Name": resource_cluster_name})
            cluster_tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
            cluster_tags_list.update(resource_mandatory_tags)

            # Get EKS Cluster IAM Role
            this_cluster_iam_role = aws_iam_role_arn[str(resource_cluster_role_arn)]

            # Getting the list of subnets needed for EKS Cluster
            eks_cluster_subnets_list = []
            for each_eks_cluster_subnet in resource_cluster_subnets:
                eks_cluster_subnets_list.append(aws_subnet_id[str(each_eks_cluster_subnet)])

            # Getting security groups for EKS Cluster
            eks_cluster_security_groups_list = []
            for each_eks_cluster_security_group in resource_cluster_security_groups:
                eks_cluster_security_groups_list.append(aws_sgs_ids[str(each_eks_cluster_security_group)])

            # Getting the list of public access cidrs for EKS Cluster
            eks_cluster_public_access_cidrs_list = []
            for each_eks_cluster_public_access_cidr in resource_cluster_public_access_cidrs:
                eks_cluster_public_access_cidrs_list.append(str(each_eks_cluster_public_access_cidr))


            eks_cluster = eks.Cluster(

                resource_cluster_name,
                name            = resource_cluster_name,
                version         = resource_cluster_version,
                role_arn        = this_cluster_iam_role,
                vpc_config      = {

                    'endpoint_private_access'   : resource_cluster_endpoint_private_access,
                    'endpoint_public_access'    : resource_cluster_endpoint_public_access,
                    'subnet_ids'                : eks_cluster_subnets_list,
                    'security_group_ids'        : eks_cluster_security_groups_list,
                    'publicAccessCidrs'         : eks_cluster_public_access_cidrs_list,

                },
                tags            = cluster_tags_list

            )

            pulumi.export(eks_cluster._name, [

                    eks_cluster.id,
                    eks_cluster.arn,
                    eks_cluster.endpoint,
                    eks_cluster.certificate_authority

                ]

            )


            #
            # EKS Node Groups
            #

            for eks_nodegroup_name, eks_nodegroup_configuration in eks_cluster_configuration["nodegroup"].items():

                # AWS EKS Node Group Dynamic Variables
                resource_nodegroup_name                 = eks_nodegroup_name

                resource_nodegroup_role_arn             = eks_nodegroup_configuration["role"]                       if "role"               in eks_nodegroup_configuration else None
                resource_nodegroup_subnets              = eks_nodegroup_configuration["subnets"]                    if "subnets"            in eks_nodegroup_configuration else None
                resource_nodegroup_instance_type        = eks_nodegroup_configuration["instance_type"]              if "instance_type"      in eks_nodegroup_configuration else None
                resource_nodegroup_instance_disk_size   = eks_nodegroup_configuration["instance_disk_size"]         if "instance_disk_size" in eks_nodegroup_configuration else 40
                resource_nodegroup_desired_size         = eks_nodegroup_configuration["scaling"]["desired_size"]    if "desired_size"       in eks_nodegroup_configuration["scaling"] else 3
                resource_nodegroup_max_size             = eks_nodegroup_configuration["scaling"]["max_size"]        if "max_size"           in eks_nodegroup_configuration["scaling"] else 3
                resource_nodegroup_min_size             = eks_nodegroup_configuration["scaling"]["min_size"]        if "min_size"           in eks_nodegroup_configuration["scaling"] else 3

                resource_tags                           = None
                resource_tags                           = eks_nodegroup_configuration["tags"] if "tags" in eks_nodegroup_configuration else None

                # Getting list of tags from configuration file
                nodegroup_tags_list = {}
                if resource_tags is not None:
                    for each_tag_name, each_tag_value in resource_tags.items():
                        nodegroup_tags_list.update({each_tag_name: each_tag_value})

                # Adding mandatory tags
                nodegroup_tags_list.update({"Name": resource_nodegroup_name})
                nodegroup_tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
                nodegroup_tags_list.update(resource_mandatory_tags)

                # Getting the list of subnets needed for EKS Node Group
                eks_nodegroup_subnets_list = []
                if resource_nodegroup_subnets is not None:
                    for each_eks_nodegroup_subnet in resource_nodegroup_subnets:
                        eks_nodegroup_subnets_list.append(aws_subnet_id[str(each_eks_nodegroup_subnet)])

                # Get EKS Node Group IAM Role
                this_nodegroup_iam_role         = aws_iam_role_arn[str(resource_nodegroup_role_arn)]

                eks_node_group = eks.NodeGroup(

                    resource_nodegroup_name,
                    cluster_name        = eks_cluster.name,
                    node_group_name     = resource_nodegroup_name,
                    version             = resource_cluster_version,
                    node_role_arn       = this_nodegroup_iam_role,
                    subnet_ids          = eks_nodegroup_subnets_list,
                    instance_types      = resource_nodegroup_instance_type,
                    disk_size           = resource_nodegroup_instance_disk_size,
                    scaling_config      = eks.NodeGroupScalingConfigArgs(
                        desired_size    = resource_nodegroup_desired_size,
                        max_size        = resource_nodegroup_max_size,
                        min_size        = resource_nodegroup_min_size,
                    ),
                    tags                = nodegroup_tags_list

                )

                # Export
                pulumi.export(eks_node_group._name, eks_node_group.id)
