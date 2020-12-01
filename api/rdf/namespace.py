from rdflib.namespace import ClosedNamespace
from rdflib.term import URIRef

PHENO = ClosedNamespace(
    uri=URIRef("http://phenomebrowser.net/"),
    terms=[
        #Classes
        "Disease", "Drug", "Device", "Gene", "Genotype",
        "Phenotype", "Pathogen", "Provenance", "Association", "Metabolite",
        "AssociationSet", 

        #Properties
        "url", "includeTypes", "association"
    ]
)

OBO = ClosedNamespace(
    uri=URIRef("http://purl.obolibrary.org/obo/"),
    terms=[
        #has evidence
        "RO_0002558",
        #has phenotype
        "RO_0002200",
        #phenotypic similarity evidence used in automatic assertion
        "ECO_0007824",
        #curator inference used in manual assertion (manually curated)
        "ECO_0000305",
        #similarity evidence used in automatic assertion
        "ECO_0000251",
        #computational evidence used in automatic assertion (text mining, lexical matching, based on NPMI value)
        "ECO_0007669",
        #evidence used in automatic assertion (IEA)
        "ECO_0000501",
        # author statement from published clinical study (PCS for published clinical study)
        "ECO_0006016",
        # inference based on individual clinical experience (ICS for individual clinical experience)
        "ECO_0006018",
        #author statement supported by traceable reference (TAS traceable author statement) 
        "ECO_0000033",
        #associated with
        "PATO_0001668"
    ]
)

PUBCHEM = ClosedNamespace(uri=URIRef("https://pubchem.ncbi.nlm.nih.gov/compound/"), terms=[])
MGI = ClosedNamespace(uri=URIRef("http://www.informatics.jax.org/marker/"), terms=[])
ENTREZ_GENE = ClosedNamespace(uri=URIRef("https://www.ncbi.nlm.nih.gov/gene/"), terms=[])
DECIPHER = ClosedNamespace(uri=URIRef("https://decipher.sanger.ac.uk/syndrome/"), terms=[])
OMIM = ClosedNamespace(uri=URIRef("https://omim.org/entry/"), terms=[])
ORPHA = ClosedNamespace(uri=URIRef("http://www.orpha.net/ORDO/Orphanet_"), terms=[])
PMID = ClosedNamespace(uri=URIRef("https://www.ncbi.nlm.nih.gov/pubmed/"), terms=[])
ISBN = ClosedNamespace(uri=URIRef("https://isbnsearch.org/isbn/"), terms=[])

RDFLIB_FORMAT_DIC = {
    'xml' : 'rdf', 'n3': 'n3', 'turtle': 'ttl', 'nt': 'nt', 'pretty-xml': 'rdf', 'trix': 'trix', 'trig': 'trig', 'nquads':'nquads'
}

PREFIX_TO_TYPE_DICT = {
    (str(OBO.uri) + 'HP' ): str(PHENO.Phenotype),
    (str(OBO.uri) + 'MP' ): str(PHENO.Phenotype),
    (str(OBO.uri) + 'GO' ): str(PHENO.Gene),
    (str(OBO.uri) + 'NCBITAXON' ): str(PHENO.Pathogen),
    (str(OBO.uri) + 'CHEBI' ): str(PHENO.Metabolite),
    (str(OBO.uri) + 'DOID' ): str(PHENO.Disease),
    str(ORPHA.uri): str(PHENO.Disease),
    str(DECIPHER.uri): str(PHENO.Disease),
    str(OMIM.uri): str(PHENO.Disease),
    str(PUBCHEM.uri): str(PHENO.Drug),
    str(MGI.uri): str(PHENO.Gene),
    str(ENTREZ_GENE.uri): str(PHENO.Gene)
} 

PREFIX_TO_VALUESET_DICT = {
    (str(OBO.uri) + 'HP_' ): 'HP',
    (str(OBO.uri) + 'MP_' ): 'MP',
    (str(OBO.uri) + 'NCBITAXON_' ): 'NCBITAXON',
    (str(OBO.uri) + 'CHEBI_' ): 'CHEBI',
    (str(OBO.uri) + 'DOID_' ): 'DOID',
    str(ORPHA.uri): 'ordo',
    str(OMIM.uri): 'OMIM',
    str(DECIPHER.uri): 'DECIPHER',
    str(MGI.uri): 'MGI',
    str(ENTREZ_GENE.uri): 'NCBIGene',
    str(PUBCHEM.uri): 'PUBCHEM',
} 

def find_type(uri):
    for key in PREFIX_TO_TYPE_DICT:
        if key in uri:
            return PREFIX_TO_TYPE_DICT[key] 
    return 'entity'

def find_valueset(uri):
    for key in PREFIX_TO_VALUESET_DICT:
        if key in uri:
            return PREFIX_TO_VALUESET_DICT[key] 
    return None