import api.rdf.virtuoso as virt
import logging

logger = logging.getLogger(__name__)

class Association:
    MIME_TYPE_JSON = "application/json"

    def find(self, concept_iri, phenotype_iri, concept_type_iri=None):
        if not concept_iri and not phenotype_iri:
           raise RuntimeException("atleast one of concept and phenotype field is required")
        
        phenotype_stmt = ('?association rdf:predicate obo:RO_0002200 . \
            ?association rdf:object <' + phenotype_iri + '> . \
            ?association rdf:subject ?concept .') if phenotype_iri and not concept_iri else ''

        concept_stmt = ('?association rdf:subject <' + concept_iri + '> . \
            ?association rdf:predicate obo:RO_0002200 . \
            ?association rdf:object ?phenotype .') if concept_iri and not phenotype_iri else ''
        
        type_subj = '?concept' if not concept_iri else '<{iri}>'.format(iri=concept_iri)
        type_stmt = (type_subj + ' rdf:type <' + concept_type_iri + '> .' ) if concept_type_iri else type_subj + ' rdf:type  ?conceptType .'

        concept_var = '?concept' if not concept_iri else '(<{iri}> as ?concept)'.format(iri=concept_iri)
        type_var = '?conceptType' if not concept_type_iri else '(<{iri}> as ?conceptType)'.format(iri=concept_type_iri)
        phenotype_var = '?phenotype' if not phenotype_iri else '(<{iri}> as ?phenotype)'.format(iri=phenotype_iri)
        query = 'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
                PREFIX pb: <http://phenomebrowser.net/> \
                PREFIX obo: <http://purl.obolibrary.org/obo/> \
                PREFIX dcterms: <http://purl.org/dc/terms/> \
                PREFIX dc: <http://purl.org/dc/elements/1.1/> \
                \
                SELECT ?association ' + concept_var + ' ' + type_var + ' ' + phenotype_var + ' ?evidence ?creator (group_concat(distinct ?source;separator=",") as ?sources) ?created \
                FROM <http://phenomebrowser.net> \
                WHERE { \
                    ?association rdf:type rdf:Statement . \
                    ' + phenotype_stmt + ' \
                    ' + concept_stmt + ' \
                    ' + type_stmt + ' \
                    ?association obo:RO_0002558 ?evidence . \
                    ?association dc:provenance ?prov . \
                    ?prov dc:creator ?creator . \
                    ?prov dcterms:source ?source . \
                    OPTIONAL { ?prov dcterms:created ?created . } \
                }'
        logger.debug("Executing query for search criteria: concept_iri=" 
            + str(concept_iri) + "|phenotype_iri=" + str(phenotype_iri) + "|concept_type_iri=" + str(concept_type_iri))
        # logger.debug("Query : %s", query)  
        return virt.execute_sparql(query, self.MIME_TYPE_JSON)

    def find_concepts(self, concept_iris):
        concept_iris_str = ''
        for iri in concept_iris:
            concept_iris_str = concept_iris_str + '<' + iri + '> '
        query = 'PREFIX pb: <http://phenomebrowser.net/> \
                select ?concept ?type \
                from <http://phenomebrowser.net> { \
                    values ?concept { ' + concept_iris_str + '} . \
                    ?concept a ?type . \
                }' 
        logger.debug("Executing query for search criteria: concept_iris=" + concept_iris_str)
        return virt.execute_sparql(query, self.MIME_TYPE_JSON)
