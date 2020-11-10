#
# NOTE: Incomplete module
#

import  pulumi

from    sys         import path
from    os          import getenv
from    pulumi_aws  import ec2

from parse              import ParseYAML
from aws.mandatory      import Mandatory

# General variables
resource_type           = "acm"
resource_project        = getenv('IAC__PROJECT_ID')
resource_mandatory_tags = Mandatory.Tags()

# Resource dictionary
acm_ids_dict = {}

class ACM:

    def __init__(self):

        resource_specs  = ParseYAML(resource_type).getSpecs()

        for acm_name, acm_configuration in resource_specs.items():

            # AWS ACM Dynamic Variables
            resource_name                   = acm_name
            resource_number_of_instances    = acm_configuration["domain"]
            resource_namespace              = acm_configuration["validation_type"]