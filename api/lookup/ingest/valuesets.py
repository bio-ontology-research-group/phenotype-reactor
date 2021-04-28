from api.lookup.ingest.aberowl_valueset import AberowlValueset

class HP(AberowlValueset):
    def __init__(self):
        super().__init__("HP", "Phenotype")

class MP(AberowlValueset):
    def __init__(self):
        super().__init__("MP", "Phenotype")

class ORDO(AberowlValueset):
    def __init__(self):
        super().__init__("ordo", "Disease")

class NCBITAXON(AberowlValueset):
    def __init__(self):
        super().__init__("NCBITAXON", "Pathogen")

class DOID(AberowlValueset):
    def __init__(self):
        super().__init__("DOID", "Disease")

class MONDO(AberowlValueset):
    def __init__(self):
        super().__init__("MONDO", "Disease")
    

    def map_entity(self, entity):
        if self.name + '_' not in entity['class']:
            return None

        return super().map_entity(entity)

class CHEBI(AberowlValueset):
    def __init__(self):
        super().__init__("CHEBI", "Metabolite")

class ECO(AberowlValueset):
    def __init__(self):
        super().__init__("ECO", "Evidence")
class NCIT(AberowlValueset):
    def __init__(self):
        super().__init__("NCIT", "Cancer_terms")
class GO(AberowlValueset):
    def __init__(self):
        super().__init__("GO", "Functions", True)