import api.virtuoso as virt

class Association:

    MIME_TYPE_JSON = "application/json"
    
    def findPhenotypeAssociations(concept_iri, concept_type_iri=None):
        query = ''
        return

    def findConceptAssociation(phenotype_iri, concept_type_iri=None):
        type_stmt = ('?concept rdf:type <' + concept_type_iri + '> .' ) if concept_type_iri else ''
        query = 'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
                PREFIX pb: <http://phenomebrowser.net/> \
                PREFIX obo: <http://purl.obolibrary.org/obo/> \
                PREFIX dcterms: <http://purl.org/dc/terms/> \
                PREFIX dc: <http://purl.org/dc/elements/1.1/> \
                \
                SELECT ?association ?concept ?creator ?source \
                FROM <http://phenomebrowser.net> \
                WHERE { \
                    ?association rdf:type rdf:Statement . \
                    ?association rdf:predicate obo:RO_0002200 . \
                    ?association rdf:object <{phenotype_iri}> . \
                    ?association rdf:subject ?concept . \
                    {type_stmt} \
                    ?association dc:provenance ?prov . \
                    ?prov dc:creator ?creator . \
                    ?prov dcterms:source ?source . \
                }'.format(phenotype_iri=phenotype_iri, type_stmt=type_stmt)
        return virt.execute_sparql(query, self.MIME_TYPE_JSON)