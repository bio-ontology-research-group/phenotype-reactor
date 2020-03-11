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
        super().__init__("NCBITAXON", "Pahtogen")

class DOID(AberowlValueset):
    def __init__(self):
        super().__init__("DOID", "Disease")

class MONDO(AberowlValueset):
    def __init__(self):
        super().__init__("MONDO", "Disease")

class CHEBI(AberowlValueset):
    def __init__(self):
        super().__init__("CHEBI", "Metabolite")