import  pulumi

from    sys         import path
from    os          import getenv
from    pulumi_aws  import ec2

from parse              import ParseYAML
from aws.mandatory      import Mandatory