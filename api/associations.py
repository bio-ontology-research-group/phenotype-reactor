import api.rdf.virtuoso as virt
import logging

logger = logging.getLogger(__name__)

class Associations:
    MIME_TYPE_JSON = "application/json"

    def find(self, concept_iri, phenotype_iri, concept_type_iri=None, evidence_iris=[], associationset_iri=None, limit=10, offset=None, order_by=None):
        if not concept_iri and not phenotype_iri:
           raise RuntimeException("atleast one of concept and phenotype field is required")
        
        phenotype_stmt = ('\n    ?association rdf:predicate obo:RO_0002200 . \
            \n    ?association rdf:object <' + phenotype_iri + '> . \
            \n    <' + phenotype_iri + '>  rdfs:label ?phenotypeLabel . \
            \n    ?association rdf:subject ?concept . \
            \n    ?concept rdfs:label ?conceptLabel .') if phenotype_iri and not concept_iri else ''

        concept_stmt = ('\n    ?association rdf:subject <' + concept_iri + '> . \
            \n    <' + concept_iri + '>  rdfs:label ?conceptLabel . \
            \n    ?association rdf:predicate obo:RO_0002200 . \
            \n    ?association rdf:object ?phenotype . \
            \n    ?phenotype rdfs:label ?phenotypeLabel .') if concept_iri and not phenotype_iri else ''
        
        type_subj = '?concept' if not concept_iri else '<{iri}>'.format(iri=concept_iri)
        type_stmt = (type_subj + ' rdf:type <' + concept_type_iri + '> .' ) if concept_type_iri else type_subj + ' rdf:type  ?conceptType .'

        associationset_stmt = ('<' + associationset_iri + '>' if associationset_iri else '?associationset') + ' pb:association ?association .' 
        associationsetLabel_stmt = ('<' + associationset_iri + '>' if associationset_iri else '?associationset') + ' rdfs:label ?associationsetLabel .'

        concept_var = '?concept' if not concept_iri else '(<{iri}> as ?concept)'.format(iri=concept_iri)
        type_var = '?conceptType' if not concept_type_iri else '(<{iri}> as ?conceptType)'.format(iri=concept_type_iri)
        associationset_var = '?associationset' if not associationset_iri else '(<{iri}> as ?associationset)'.format(iri=associationset_iri)
        phenotype_var = '?phenotype' if not phenotype_iri else '(<{iri}> as ?phenotype)'.format(iri=phenotype_iri)

        order_clause = self.create_orderby_clause(order_by)
        page = order_clause + ' LIMIT ' + str(limit) + " OFFSET " + str(offset) if offset else ''
        graph_pattern = 'WHERE { \
                \n    ?association rdf:type rdf:Statement . \
                    ' + phenotype_stmt + ' \
                    ' + concept_stmt + ' \
                \n    ' + type_stmt + ' \
                \n    ' + associationset_stmt + ' \
                \n    ' + associationsetLabel_stmt + ' \
                \n    ' + self.evidence_stmt(evidence_iris) + ' \
                \n    ?evidence rdfs:label ?evidenceLabel . \
                \n    ?association dc:provenance ?prov . \
                \n    ?prov dc:creator ?creator . \
                \n    ?prov dcterms:source ?source . \
                \n    OPTIONAL { ?prov dcterms:created ?created . } \
                \n}'
        query = 'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
                \nPREFIX pb: <http://phenomebrowser.net/> \
                \nPREFIX obo: <http://purl.obolibrary.org/obo/> \
                \nPREFIX dcterms: <http://purl.org/dc/terms/> \
                \nPREFIX dc: <http://purl.org/dc/elements/1.1/> \
                \n\
                \nSELECT * \
                \n{\n { \
                \n  SELECT ?association ' + concept_var + ' ' + type_var + ' ' + phenotype_var + ' ?phenotypeLabel ?conceptLabel \
                \n  ?evidence ?evidenceLabel ?creator (group_concat(distinct ?source;separator=",") as ?sources) ?created \
                \n  ' + associationset_var + ' ?associationsetLabel \
                \n  FROM <http://phenomebrowser.net> \
                \n  ' + graph_pattern + page + ' \
                \n  } \
                \n  UNION { select (count(*) as ?total)  \
                \n  FROM <http://phenomebrowser.net> \
                \n  ' + graph_pattern + ' \
                \n  }\n}'
        logger.debug("Executing query for search criteria: concept_iri=" 
            + str(concept_iri) + "|phenotype_iri=" + str(phenotype_iri) + "|concept_type_iri=" + str(concept_type_iri))
        # logger.debug("Query : %s", query)  
        return (virt.execute_sparql(query, self.MIME_TYPE_JSON), query)

    def find_similar_concepts(self, concept_iri, type_iri, order_by, limit = 100):
        order_clause = self.create_orderby_clause(order_by)
        query = 'PREFIX b2v: <http://bio2vec.net/function#> \
                \nPREFIX b2vd: <http://bio2vec.net/dataset#> \
                \n \
                \nSELECT ?concept ?conceptLabel ?type ?val ?x ?y \
                \nWHERE { \
                \n    SERVICE <https://bio2vec.cbrc.kaust.edu.sa/ds/query> {  \
                \n        (?concept ?val ?x ?y) b2v:mostSimilar(b2vd:dataset_4 <' + concept_iri + '> ' + str(limit) + ' ' \
                            + (('<' + type_iri + '>' ) if type_iri else '') + ') .  \
                \n    }  \
                \n    GRAPH <http://phenomebrowser.net> { \
                \n        ?concept a ?type . \
                \n        OPTIONAL { ?concept rdfs:label ?conceptLabel } .\
                \n    } \
                \n}' + order_clause
        logger.debug("Executing query for search criteria: concept_iri=" + concept_iri)
        return (virt.execute_sparql(query, self.MIME_TYPE_JSON), query)
    
    def find_common_phenotypes(self, source_iri, target_iri):
        query = 'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
                \nPREFIX pb: <http://phenomebrowser.net/> \
                \nPREFIX obo: <http://purl.obolibrary.org/obo/> \
                \nSELECT ?phenotype ?phenotypeLabel \
                \nFROM <http://phenomebrowser.net> \
                \nWHERE { \
                \n  <' + source_iri + '> obo:RO_0002200 ?phenotype . \
                \n  <' + target_iri + '> obo:RO_0002200 ?phenotype . \
                \n  ?phenotype rdfs:label ?phenotypeLabel . \
                \n} ORDER BY asc(?phenotypeLabel)'
        logger.debug("Executing find all associationset query")
        return (virt.execute_sparql(query, self.MIME_TYPE_JSON), query)

    def create_orderby_clause(self, order_by):
        order_clause = ''
        if order_by :
            order_clause += f' ORDER BY '
            if ":":
                parts = order_by.split(":")
                order_clause +=  f'{parts[0]}(?{parts[1]})'
            else:
                order_clause += f'asc(?{order_by})'
        return order_clause

    def evidence_stmt(self, evidence_iris):
        stmt = '?association obo:RO_0002558 ?evidence .'
        if len(evidence_iris) < 1:
            return stmt
        
        return "values ?evidence " + self.values_content(evidence_iris) + " . \
        \n    " + stmt



    def values_content(self, values):
        stmt = "{"
        for val in values:
            stmt += f' <{val}>'
        stmt += " }"
        return stmt