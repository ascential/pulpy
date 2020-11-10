import  pulumi
from    sys         import path
from    os          import getenv
from    pulumi_aws  import route53

# Custom packages
from parse          import ParseYAML
from aws.mandatory  import Mandatory
from aws.vpc        import VPCs

# General variables
resource_type           = "route53"
resource_project        = getenv('IAC__PROJECT_ID')
resource_mandatory_tags = Mandatory.Tags()

# Resource dictionaries
route53_public_zone_ids_dict    = {}
route53_private_zone_ids_dict   = {}
route53_record_ids_dict         = {}


class Route53:


#
# Route53 Public Zone
#


    @classmethod
    def PublicZone(self):

        resource_specs = ParseYAML(resource_type).getSpecs()

        for r53_public_zone_name, r53_public_zone_configuration in resource_specs["public-zone"].items():

            # Route53 Public Dynamic Variables
            resource_name       = r53_public_zone_name

            # Resetting all optional variables
            # with the default value None
            resource_comment    = \
            resource_tags       = None


            # Cheking the documents content, if present
            # we will be assigning their values to our variables,
            # otherwise we'll set them to None
            resource_comment    = r53_public_zone_configuration["comment"]  if "comment"    in r53_public_zone_configuration else None
            resource_tags       = r53_public_zone_configuration["tags"]     if "tags"       in r53_public_zone_configuration else None

            # Getting list of tags from configuration file
            tags_list               = {}
            if resource_tags is not None:
                for each_tag_name, each_tag_value in resource_tags.items():
                    tags_list.update({each_tag_name: each_tag_value})

            # Adding mandatory tags
            tags_list.update({"Name": resource_name})
            tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
            tags_list.update(resource_mandatory_tags)

            # Create Route53 Public Zone
            route53_public_zone = route53.Zone(

                resource_name,
                name        = resource_name,
                comment     = resource_comment,
                tags        = tags_list

            )

            pulumi.export(
                resource_name,
                    [
                        {
                            "ID"            : route53_public_zone.id,
                            "Name servers"  : route53_public_zone.name_servers,
                            "Zone ID"       : route53_public_zone.zone_id
                        }
                    ]
            )

            route53_public_zone_ids_dict.update({route53_public_zone._name: route53_public_zone.id})

    @classmethod
    def PublicZoneId(cls):

        return route53_public_zone_ids_dict


#
# Route53 Private Zone
#


    @classmethod
    def PrivateZone(self):

        resource_specs  = ParseYAML(resource_type).getSpecs()

        aws_vpc_id      = VPCs.VPCId()

        for r53_private_zone_name, r53_private_zone_configuration in resource_specs["private-zone"].items():

            # Route53 Private Zone Dynamic Variables
            resource_name       = r53_private_zone_name

            # Resetting all optional variables
            # with the default value None
            resource_comment    = \
            resource_vpcs       = \
            resource_tags       = None


            # Cheking the documents content, if present
            # we will be assigning their values to our variables,
            # otherwise we'll set them to None
            resource_comment    = r53_private_zone_configuration["comment"] if "comment"    in r53_private_zone_configuration else None
            resource_vpcs       = r53_private_zone_configuration["vpcs"]    if "vpcs"       in r53_private_zone_configuration else None
            resource_tags       = r53_private_zone_configuration["tags"]    if "tags"       in r53_private_zone_configuration else None

            # Getting list of tags from configuration file
            tags_list               = {}
            if resource_tags is not None:
                for each_tag_name, each_tag_value in resource_tags.items():
                    tags_list.update({each_tag_name: each_tag_value})

            # Adding mandatory tags
            tags_list.update({"Name": resource_name})
            tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
            tags_list.update(resource_mandatory_tags)

            # Get the list of VPCs
            resource_vpcs_list = []

            for each_private_zone_vpc in (resource_vpcs):

                this_vpc = aws_vpc_id[str(each_private_zone_vpc)]
                # this_vpc = aws_vpc_id[str(each_private_zone_vpc)]
                # resource_vpcs_list.append(each_private_zone_vpc)

                resource_vpcs_list.append(this_vpc)

            print(resource_vpcs_list)

            # Create Route53 Private Zone
            route53_private_zone = route53.Zone(

                resource_name,
                name        = resource_name,
                comment     = resource_comment,
                # vpcs        = resource_vpcs_list,
                tags        = tags_list
                # vpcs        = [
                #     route53.ZoneVpcArgs(
                #         vpc_id = resource_vpcs_list
                #     )
                # ]

            )

            pulumi.export(
                resource_name,
                (
                    route53_private_zone.id,
                    route53_private_zone.name_servers,
                    route53_private_zone.zone_id,
                )
            )

            route53_private_zone_ids_dict.update({route53_private_zone._name: route53_private_zone.id})


    @classmethod
    def PrivateZoneId(cls):

        return route53_private_zone_ids_dict


#
# Route53 Record
#


    @classmethod
    def Record(self):

        resource_specs = ParseYAML(resource_type).getSpecs()

        for r53_record_name, r53_record_configuration in resource_specs["record"].items():

            # Route53 Record Dynamic Variables
            resource_name       = r53_record_name

            # Resetting all optional variables
            # with the default value None
            resource_record_type    = \
            resource_record_zone_id = \
            resource_record_target  = \
            resource_record_ttl     = None

            # Cheking the documents content, if present
            # we will be assigning their values to our variables,
            # otherwise we'll set them to None
            resource_record_type        = r53_record_configuration["type"]      if "type"       in r53_record_configuration else None
            resource_record_zone_type   = r53_record_configuration["zone_type"] if "zone_type"  in r53_record_configuration else None
            resource_record_zone_id     = r53_record_configuration["zone_name"] if "zone_name"  in r53_record_configuration else None
            resource_record_target      = r53_record_configuration["target"]    if "target"     in r53_record_configuration else None
            resource_record_ttl         = r53_record_configuration["ttl"]       if "ttl"        in r53_record_configuration else None

            # Check record value type
            for each_record_target_type, each_record_target_value in resource_record_target.items():

                # print(each_record_target_type)

                if each_record_target_type.lower() == "cname":
                    resource_record_value = each_record_target_value

                elif each_record_target_type.lower() == "a":
                    resource_record_value = each_record_target_value

                elif each_record_target_type.lower() == "eip":
                    resource_record_value = each_record_target_value

                elif each_record_target_type.lower() == "ec2":
                    resource_record_value = each_record_target_value

            # Get ZoneId being Public or Private
            if resource_record_zone_type.lower() == "public":

                route53_zone_id = Route53.PublicZoneId()
                this_route53_zone_id = route53_zone_id[str(resource_record_zone_id)]

            elif resource_record_zone_type.lower() == "private":

                route53_zone_id = Route53.PrivateZoneId()
                this_route53_zone_id = route53_zone_id[str(resource_record_zone_id)]

            # Create Route53 Record
            route53_record = route53.Record(

                resource_name,
                name    = resource_name,
                type    = resource_record_type,
                zone_id = this_route53_zone_id,
                records = [resource_record_value],
                ttl     = resource_record_ttl

            )

            pulumi.export(
                resource_name,
                    [
                        {
                            "ID"    : route53_record.id,
                            "FQDN"  : route53_record.fqdn
                        }
                    ]
            )

            route53_record_ids_dict.update({route53_record._name: route53_record.id})


    @classmethod
    def RecordId(cls):

        return route53_record_ids_dict
