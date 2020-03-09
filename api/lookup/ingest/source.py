from django.conf import settings

class Source:

    def __init__(self, name, entity_type) :
        self.sourcedir = settings.SOURCE_DATA_DIR
        self.data = None
        self.name = name
        self.entity_type = entity_type

    def fetch(self):
        # Abstract method
        raise NotImplementedError

    def map(self):
        # Abstract method
        raise NotImplementedError


    def write(self):
        # Abstract method
        raise NotImplementedError

    def get_name(self):
        return self.name