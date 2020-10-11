import  pulumi
from    sys         import path
from    os          import getenv
from    pulumi_aws  import iam

# Custom packages
from parse          import ParseYAML
from aws.mandatory  import Mandatory

# General variables
resource_type           = "iam"
resource_project        = getenv('IAC__PROJECT_ID')
resource_mandatory_tags = Mandatory.Tags()

# Resource dictionaries
iam_group_ids_dict      = {}
iam_group_arns_dict     = {}
iam_user_ids_dict       = {}
iam_user_arns_dict      = {}
iam_role_ids_dict       = {}
iam_role_arns_dict      = {}
iam_policy_ids_dict     = {}
iam_policy_arns_dict    = {}
class IAM:


#
# IAM Groups
#


    @classmethod
    def Groups(self):
        pass

    @classmethod
    def GroupId(cls):
        pass

    @classmethod
    def GroupARN(cls):
        pass


#
# IAM Users
#

    @classmethod
    def Users(self):

        resource_specs = ParseYAML(resource_type).getSpecs()

        for iam_user_name, iam_user_configuration in resource_specs["user"].items():

            # IAM User Dynamic Variables
            resource_name           = iam_user_name

            # Resetting all optional variables
            # with the default value None
            resource_user_path              = \
            resource_user_access_keys       = \
            resource_user_inline_policy     = \
            resource_user_iam_policy        = None

            # Cheking the documents content, if present
            # we will be assigning their values to our variables,
            # otherwise we'll set them to None
            resource_user_path              = iam_user_configuration["path"]            if "path"           in iam_user_configuration else None
            resource_user_access_keys       = iam_user_configuration["access-keys"]     if "access-keys"    in iam_user_configuration else None
            resource_user_inline_policy     = iam_user_configuration["user-policies"]   if "user-policies"  in iam_user_configuration else None
            resource_user_iam_policy        = iam_user_configuration["iam-policies"]    if "iam-policies"   in iam_user_configuration else None

            resource_tags                   = None
            resource_tags                   = iam_user_configuration["tags"] if "tags" in iam_user_configuration else None

            # Getting list of tags from configuration file
            tags_list               = {}
            if resource_tags is not None:
                for each_tag_name, each_tag_value in resource_tags.items():
                    tags_list.update({each_tag_name: each_tag_value})

            # Adding mandatory tags
            tags_list.update({"Name": resource_name})
            tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
            tags_list.update(resource_mandatory_tags)

            # Create IAM User
            iam_user = iam.User(

                resource_name,
                path        = resource_user_path,
                tags        = tags_list

            )

            pulumi.export(
                resource_name,
                (
                    iam_user.id,
                    iam_user.arn,
                    iam_user.unique_id
                )
            )

            iam_user_ids_dict.update({iam_user._name: iam_user.id})
            iam_user_arns_dict.update({iam_user._name: iam_user.arn})


            # Create Inline User Policy
            if resource_user_inline_policy is not None:

                for resource_user_inline_policy_key, resource_user_inline_policy_value in resource_user_inline_policy.items():

                    user_policy = iam.UserPolicy(

                        resource_user_inline_policy_key,
                        user    = iam_user.name,
                        policy  = resource_user_inline_policy_value

                    )

            # Create CLI / Programmatic Access Key
            if resource_user_access_keys is not None:

                for resource_user_access_keys_key in resource_user_access_keys:

                    user_access_key = iam.AccessKey(

                        resource_user_access_keys_key,
                        user = iam_user.name

                        )

                    #
                    # WARNING!
                    #

                    pulumi.export(

                        resource_user_access_keys_key,

                        (
                            user_access_key.user,
                            user_access_key.id,
                            user_access_key.secret,
                            # user_access_key.encrypted_secret,
                        )

                    )

    @classmethod
    def UserId(cls):

        return iam_user_ids_dict

    @classmethod
    def UserARN(cls):

        return iam_user_arns_dict


#
# IAM Roles
#


    @classmethod
    def Roles(self):

        resource_specs = ParseYAML(resource_type).getSpecs()

        for iam_role_name, iam_role_configuration in resource_specs["role"].items():

            # AWS IAM Role Dynamic Variables
            resource_name               = iam_role_name
            resource_description        = iam_role_configuration["description"]
            resource_assume_role_policy = iam_role_configuration["assume_role_policy"]

            resource_tags               = None
            resource_tags               = iam_role_configuration["tags"] if "tags" in iam_role_configuration else None

            # Getting list of tags from configuration file
            tags_list               = {}
            if resource_tags is not None:
                for each_tag_name, each_tag_value in resource_tags.items():
                    tags_list.update({each_tag_name: each_tag_value})

            # Adding mandatory tags
            tags_list.update({"Name": resource_name})
            tags_list.update({"Project/Stack": pulumi.get_project() + "/" + pulumi.get_stack()})
            tags_list.update(resource_mandatory_tags)

            # Create Role
            iam_role          = iam.Role(

                resource_name,
                description         = resource_description,
                assume_role_policy  = resource_assume_role_policy,
                tags                = tags_list

            )

            # Role policies list
            role_policies_list              = {}

            # Check if Keys are present
            resource_role_managed_policies  = \
            resource_role_custom_policies   = None

            resource_role_managed_policies  = iam_role_configuration["policies"]["managed"] if "managed" in iam_role_configuration["policies"] else None
            resource_role_custom_policies   = iam_role_configuration["policies"]["custom"] if "custom" in iam_role_configuration["policies"] else None


            # Getting AWS managed policies
            if resource_role_managed_policies is not None:

                for each_managed_policy in resource_role_managed_policies:

                    role_policies_list.update({each_managed_policy: "arn:aws:iam::aws:policy/" + each_managed_policy})

            # Getting all custom policies
            if resource_role_custom_policies is not None:

                for each_custom_policy in resource_role_custom_policies:

                    aws_iam_policy_arn      = IAM.PolicyARN()
                    this_custom_policy_arn  = aws_iam_policy_arn[str(each_custom_policy)]

                    role_policies_list.update({each_custom_policy: this_custom_policy_arn})

            # Attach all found policies to role
            #
            # TODO:
            # Check if any policy, either managed or custom, were found
            # before attempting to invoke RolePolicyAttachment

            for each_policy_name, each_policy_arn in role_policies_list.items():

                attached_policy = iam.RolePolicyAttachment(

                    each_policy_name,
                    role        = iam_role.id,
                    policy_arn  = each_policy_arn

                )

            iam_role_ids_dict.update({iam_role._name: iam_role.id})
            iam_role_arns_dict.update({iam_role._name: iam_role.arn})

            pulumi.export(

                iam_role._name, [

                    iam_role.id,
                    iam_role.arn

                ]

            )

    @classmethod
    def RoleId(cls):

        return iam_role_ids_dict

    @classmethod
    def RoleARN(cls):

        return iam_role_arns_dict


#
# IAM Policies
#


    @classmethod
    def Policies(self):

        resource_specs = ParseYAML(resource_type).getSpecs()

        for iam_policy_name, iam_policy_configuration in resource_specs["policy"].items():

            # AWS IAM Policy Dynamic Variables
            resource_name               = iam_policy_name
            resource_description        = iam_policy_configuration["description"]
            resource_path               = iam_policy_configuration["path"]
            resource_policy_content     = iam_policy_configuration["policy_content"]

            # Create Policy
            iam_policy          = iam.Policy(

                resource_name,
                description     = resource_description,
                path            = resource_path,
                policy          = resource_policy_content

            )

            iam_policy_ids_dict.update({iam_policy._name: iam_policy.id})
            iam_policy_arns_dict.update({iam_policy._name: iam_policy.arn})

            pulumi.export(

                iam_policy._name, [

                    iam_policy.id,
                    iam_policy.arn

                ]

            )

            # # Attach existing policies
            # for each_attached_policy in iam_policy_configuration["attached_policies"]:

            #     attached_policy = iam.RolePolicyAttachment(

            #         each_attached_policy,
            #         role        = iam_role.id,
            #         policy_arn  = ("arn:aws:iam::aws:policy/" + each_attached_policy)

            #     )

            iam_policy_ids_dict.update({iam_policy._name: iam_policy.id})
            iam_policy_arns_dict.update({iam_policy._name: iam_policy.arn})

            pulumi.export(

                iam_policy._name, [

                    iam_policy.id,
                    iam_policy.arn

                ]

            )

    @classmethod
    def PolicyId(cls):

        return iam_policy_ids_dict

    @classmethod
    def PolicyARN(cls):

        return iam_policy_arns_dict
