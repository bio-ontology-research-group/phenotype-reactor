from rdflib.namespace import ClosedNamespace
from rdflib.term import URIRef

PHENO = ClosedNamespace(
    uri=URIRef("http://phenomebrowser.net/"),
    terms=[
        #Classes
        "Disease", "Drug", "Device", "Gene", "Genotype",
        "Phenotype", "Pathogen", "Provenance", "Association", "Metabolite",

        #Properties
        "url"
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
        "ECO_0000033"
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