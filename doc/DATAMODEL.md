## Data Model

Phenomebrowser data model is a common structure for capturing phenotype associations so that discovered phenotype relations from various sources can be aggregated into a single common structure.

![Data Model](data-model.png)

### Association 
An association is a statement about the relation between a biomedical entity or resource with a phenotype.

### Evidence

An information that supports the existence of an association. For evidence codes, we are using evidence classes from widely used evidence ontology (ECO). Evidence classes used in associations include:

- **ECO_0007669** computational evidence used in automatic assertion such as text mining, lexical matching, based on NPMI value
- **ECO_0000305** curator inference used in manual assertion such as manually curated 
- **ECO_0000501** evidence used in automatic assertion (IEA)
- **ECO_0006016** author statement from published clinical study (PCS for published clinical study
- **ECO_0006018** inference based on individual clinical experience (ICS for individual clinical experience)
- **ECO_0000033** author statement supported by traceable reference (TAS traceable author statement) 

### Provenance

Provenance is details about changes in creation of association including when the association was created and by whom as well as the source document.

### Phenotype
Observable characteristics of an entity.

### Has Phenotype
It is an association type between a biomedical concept and phenotype.

### Resource 
Any biomedical concept that have associated phenotypes.

### Biomedical Concept
It refers to categories in the fields of biological science and medicine such as Disease, Drug, Pathogen, Device, Gene, Genotype etc

### Device
An equipment that is used for treatment, diagnosis or prevention of conditions.

### Disease
A manifestation of a disorder.

### Pathogen
A microorganism that causes an infectious disease.

### Drug
A chemical entity that regulates a biological process.

### Gene
A genomic region that contains all sequence elements that facilitate the production of a functional transcript.

### Effective Genotype
Describes the total variation in both genomic sequence along with all genes whose expression is transiently increased or decreased  through gene-specific interventions in an experiment

### Intrinsic Genotype
Describes the variation in genomic sequence across entire genome in context of its difference from some genomic background.

### Extrinsic Genotype
Describes variation in gene expression.

### Genomic Variation Complement
Variant port of a genome which comprised of set of single locus complement containing variant.

### Variant Single Locus Complement
A set of allele at a single locus where atleast one allele is a variant.

### Variant Allele
Set of sequence variants of a gene.

### Sequence Alteration
A deviation  from a reference typically a mutation in a gene.

### Reagent Targeted Gene
Gene whose expression is targeted by gene reagents in an experiment. 
