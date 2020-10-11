import  pulumi
from    sys        import path
from    os         import getenv
from    pulumi_aws import ec2      as rtb

# Custom packages
from parse                  import ParseYAML
from aws.mandatory          import Mandatory
from aws.vpc                import VPCs
from aws.internetgateway    import InternetGateways
from aws.natgateway         import NATGateways
from aws.subnet             import Subnets

# General variables
resource_type           = "routetable"
resource_project        = getenv('IAC__PROJECT_ID')
resource_mandatory_tags = Mandatory.Tags()

# Resource dictionary
rtb_ids_dict        = {}

class RouteTables:

    def __init__(self):

        resource_specs  = ParseYAML(resource_type).getSpecs()
        aws_vpc_id      = VPCs.VPCId()
        aws_igw_id      = InternetGateways.InternetGatewayId()
        aws_natgw_id    = NATGateways.NATGatewayId()
        aws_subnet_id   = Subnets.SubnetId()

        for rtb_name, rtb_configuration in resource_specs.items():

            # AWS Route Table Variables
            resource_name   = rtb_name
            resource_vpc    = rtb_configuration["vpc"]

            resource_tags   = None
            resource_tags   = rtb_configuration["tags"] if "tags" in rtb_configuration else None

            # Getting list of tags from configuration file
            tags_list       = {}
            if resource_tags is not None:
                for each_tag_name, each_tag_value in resource_tags.items():
                    tags_list.update({each_tag_name: each_tag_value})

            # Adding mandatory tags
            tags_list.update({"Name": resource_name})
            tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
            tags_list.update(resource_mandatory_tags)

            this_vpc                = aws_vpc_id[str(resource_vpc)]

            #
            # Create Route Table
            #
            aws_rtb     = rtb.RouteTable(

                resource_name,
                vpc_id  = this_vpc,
                tags    = tags_list

            )

            rtb_ids_dict.update({aws_rtb._name: aws_rtb.id})

            # Export the name of each Route Table
            pulumi.export(aws_rtb._name, aws_rtb.id)


            #
            # Route Table Routes
            #

            # Routes list
            routes_list   = []

            for each_route_entry, each_route_entry_configuration in rtb_configuration["routes"].items():

                # NAT Gateways
                if each_route_entry_configuration["target_type"] == "nat_gateway":

                    this_natgw = aws_natgw_id[str(each_route_entry_configuration["target"])]
                    routes_list.append(rtb.Route((each_route_entry + "-route"), route_table_id = aws_rtb.id, destination_cidr_block = each_route_entry_configuration["destination"], nat_gateway_id = this_natgw))

                # Internet Gateways
                elif each_route_entry_configuration["target_type"] == "internet_gateway":

                    this_igw = aws_igw_id[str(each_route_entry_configuration["target"])]
                    routes_list.append(rtb.Route((each_route_entry + "-route"), route_table_id = aws_rtb.id, destination_cidr_block = each_route_entry_configuration["destination"], gateway_id = this_igw),)

                else:

                    print("ERROR | Unsupported 'target_type' found")


                for each_route_type in routes_list:

                    # print(each_route_entry)

                    rtb_route = (

                        each_route_type
                        # opts = pulumi.ResourceOptions(depends_on=[aws_rtb[resource_name]])

                    )


            #
            # Subnet Associations
            #

            # Checking if route-table: key is present
            resource_associated_subnet  = None
            resource_associated_subnet  = rtb_configuration["associated_subnets"] if "associated_subnets" in rtb_configuration else None

            # If the key is present then we'll get the value
            # and we'll invoke the association
            if resource_associated_subnet is not None:

                subnets_count = 0

                for each_associated_subnet in resource_associated_subnet:

                    subnets_count = subnets_count + 1

                    this_subnet = aws_subnet_id[str(each_associated_subnet)]

                    route_table_association = rtb.RouteTableAssociation(

                        (resource_name + "-rtb-as-" + str(subnets_count).zfill(2)),
                        subnet_id       = this_subnet,
                        route_table_id  = aws_rtb.id

                    )

                    # Export the name of each Route Table Association
                    pulumi.export(route_table_association._name, route_table_association.id)

    @classmethod
    def RouteTableID(cls):
        return rtb_ids_dict