from sys    import path
from os import getenv

# Custom packages
from pulpy.parser import ParseYAML

# General variables
resource_type       = "mandatory"
resource_project    = getenv('IAC__PROJECT_ID')

# Resource dictionaries
mandatory_tags_dict = {}

class Mandatory:

    @classmethod
    def MandatoryTags(self):

        mandatory  = ParseYAML(resource_type).getSpecs()

        for tag_key, tag_value in mandatory["tags"].items():

            mandatory_tags_dict.update({tag_key: tag_value})

    @classmethod
    def Tags(cls):

        Mandatory.MandatoryTags()
        return mandatory_tags_dict