import  yaml
from    os          import getenv
from    glob        import glob

# TODO:
# - Import only "must" packages and remove of all unused ones
# - Add try: catch: exception: statements where needed

class ParseYAML:

    def __init__(self, resource_type):
    # def YAML(self, resource_type):

        self.resource_type      = resource_type
        self.resource_provider  = getenv('IAC__PROJECT_PROVIDER')
        self.resource_config    = getenv('IAC__PROJECT_CONFIG_PATH')

        # Setting up the base path from
        # where to read the YAML files
        self.resource_base_path = self.resource_config + "/" + self.resource_type + "/" + "/**/"

        # Making sure that we are able to read
        # both YAML file extension types (.yaml and .yml)
        self.resource_path      = glob(self.resource_base_path + "*.yaml", recursive=True) + glob(self.resource_base_path + "*.yml", recursive=True)

    def getSpecs(self):

        # Empty dictionary that will be
        # populated from the loop below
        config_list = {}

        # Reading all YAML files from the resource folder,
        # including its subfolders
        for each_yaml_file in self.resource_path:

            # Reading the content of each individual file found
            with open(each_yaml_file, "r") as stream:

                documents   = yaml.load(stream, Loader=yaml.FullLoader)
                yaml_config = documents.get(self.resource_type)

                # Checking if the resource key is present
                # in our YAML file (stream).
                # Example:
                # s3:
                #   bucket-name:
                #     ...
                if yaml_config is not None:

                    # Creating a temporary dictionary from the
                    # current file within the loop
                    temp_dict = dict(yaml_config)

                    # Updating the main dictionary which was
                    # initiated above as being blank
                    config_list.update(temp_dict)

                # else:

                #     print("ERROR |", self.resource_provider.upper(), self.resource_type.upper(), "- No configuration file found!")


        # Returning a complete dictionary
        # back to our resource module
        return config_list