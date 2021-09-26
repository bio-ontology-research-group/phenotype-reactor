from api.rdf.namespace import find_valueset
from api.lookup.lookup_elasticsearch import find_entity_by_iris
import requests
import api.rdf.virtuoso as virt
import api.rdf.aberowl as aberowl
import logging

logger = logging.getLogger(__name__)

class Associations:
    MIME_TYPE_JSON = "application/sparql-results+json"
    PHENOME_SERVICE_URL = "http://phenomebrowser.net/sparql"

    def find(self, concept_iri, phenotype_iri, concept_type_iri=None, evidence_iris=[], associationset_iris=None, include_subclass=False, limit=10, offset=None, order_by=None):
        if not concept_iri and not phenotype_iri:
           raise RuntimeException("atleast one of concept and phenotype field is required")
        
        phenotype_stmt = self.create_phenotype_filter(phenotype_iri, concept_iri, include_subclass)
        concept_stmt = self.create_concept_filter(concept_iri, phenotype_iri)
        
        type_subj = '?concept' if not concept_iri else '<{iri}>'.format(iri=concept_iri)
        type_stmt = (type_subj + ' rdf:type <' + concept_type_iri + '> .' ) if concept_type_iri else type_subj + ' rdf:type  ?conceptType .'

        concept_var = '?concept' if not concept_iri else '(<{iri}> as ?concept)'.format(iri=concept_iri)
        type_var = '?conceptType' if not concept_type_iri else '(<{iri}> as ?conceptType)'.format(iri=concept_type_iri)
        phenotype_var = '?phenotype' if not phenotype_iri and not include_subclass else '(<{iri}> as ?phenotype)'.format(iri=phenotype_iri)

        order_clause = self.create_orderby_clause(order_by)
        page = order_clause + ' LIMIT ' + str(limit) + " OFFSET " + str(offset) if offset else ''

        graph_pattern = 'WHERE { \
                \n    ?association rdf:type rdf:Statement . \
                    ' + phenotype_stmt + ' \
                    ' + concept_stmt + ' \
                \n    ' + type_stmt + ' \
                \n    ' + self.associationset_stmt(associationset_iris) + ' \
                \n    ?associationset rdfs:label ?associationsetLabel . \
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
                \n  ?associationset ?associationsetLabel \
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
        if not include_subclass:
            return (virt.execute_sparql(query, self.MIME_TYPE_JSON), query)
        else:
            return (aberowl.execute_sparql(query, self.MIME_TYPE_JSON), query)

    def create_phenotype_filter(self, phenotype_iri, concept_iri, include_subclass):
        if phenotype_iri and include_subclass and not concept_iri:
            ontology = find_valueset(phenotype_iri)
            result = find_entity_by_iris([phenotype_iri], ontology)
            label = result[0]['label'][0]
            label = "'" + label + "'" if len(label.split(' ')) > 1 else label 
            label = label.lower()
            return ("\n    ?association rdf:predicate obo:RO_0002200 . \
                \n     VALUES ?phenotype { \
                \n		OWL subeq <" + self.PHENOME_SERVICE_URL + "> <" + ontology + "> { \
	            \n		    " + label + " \
                \n		} \
                \n	} . \
                \n    ?association rdf:object ?phenotype . \
                \n    ?phenotype rdfs:label ?phenotypeLabel . \
                \n    ?association rdf:subject ?concept . \
                \n    ?concept rdfs:label ?conceptLabel .") 


        elif phenotype_iri and not concept_iri:
            return ('\n    ?association rdf:predicate obo:RO_0002200 . \
                \n    ?association rdf:object <' + phenotype_iri + '> . \
                \n    <' + phenotype_iri + '>  rdfs:label ?phenotypeLabel . \
                \n    ?association rdf:subject ?concept . \
                \n    ?concept rdfs:label ?conceptLabel .') 
        else:
            return ''

    def create_concept_filter(self, concept_iri, phenotype_iri):
        if concept_iri and not phenotype_iri: 
            return ('\n    ?association rdf:subject <' + concept_iri + '> . \
            \n    <' + concept_iri + '>  rdfs:label ?conceptLabel . \
            \n    ?association rdf:predicate obo:RO_0002200 . \
            \n    ?association rdf:object ?phenotype . \
            \n    ?phenotype rdfs:label ?phenotypeLabel .') 
        else:
            return ''

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

    
    def find_matching_phenotypes(self, source_iri, target_iri):
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

    def find_all_phenotypes(self, concept_iri):
        query = 'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
                \nPREFIX pb: <http://phenomebrowser.net/> \
                \nPREFIX obo: <http://purl.obolibrary.org/obo/> \
                \nSELECT ?phenotype ?phenotypeLabel \
                \nFROM <http://phenomebrowser.net> \
                \nWHERE { \
                \n   <' + concept_iri + '> obo:RO_0002200 ?phenotype . \
                \n  ?phenotype rdfs:label ?phenotypeLabel . \
                \n} ORDER BY asc(?phenotypeLabel)'
        logger.debug("Executing find all phenotypes query for a concept: %s", concept_iri)
        return (virt.execute_sparql(query, self.MIME_TYPE_JSON), query)

    
    def find_matching_phenotype_superclasses(self, source_iri, target_iri):
        (source_phenos, query) = self.find_all_phenotypes(source_iri)
        (target_phenos, query) = self.find_all_phenotypes(target_iri)

        source_pheno_iris = list(map(lambda x: x['phenotype']['value'], source_phenos.json()['results']['bindings']))
        source_hp_phenos = list(filter(lambda x: 'HP_' in x, source_pheno_iris))
        source_mp_phenos = list(filter(lambda x: 'MP_' in x, source_pheno_iris))

        target_pheno_iris = list(map(lambda x: x['phenotype']['value'], target_phenos.json()['results']['bindings']))
        target_hp_phenos = list(filter(lambda x: 'HP_' in x, target_pheno_iris))
        target_mp_phenos = list(filter(lambda x: 'MP_' in x, target_pheno_iris))

        logger.debug("Executing find matching phenotype superclasses for source: %s, target: %s", source_iri, target_iri)
        matching_phenos_hp = self.request_matching_superclasses(source_hp_phenos, target_hp_phenos, 'HP')
        matching_phenos_mp = self.request_matching_superclasses(source_mp_phenos, target_mp_phenos, 'MP')

        matching_phenos = matching_phenos_hp + matching_phenos_mp
        return matching_phenos


    def request_matching_superclasses(self, source_classes, targert_classes, ontology):
        if len(source_classes) < 1 or len(targert_classes) < 1:
            return []
            
        request_data = { "source_classes": source_classes, "target_classes": targert_classes }
        url = f"http://aber-owl.net/api/ontology/{ontology}/class/_matchsuperclasses"
        result = requests.post(url, json=request_data)
        return result.json()['result']


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

    def associationset_stmt(self, associationset_iris):
        stmt = '?associationset pb:association ?association .'
        if len(associationset_iris) < 1:
            return stmt
        
        return "values ?associationset " + self.values_content(associationset_iris) + " . \
        \n    " + stmt

    def values_content(self, values):
        stmt = "{"
        for val in values:
            stmt += f' <{val}>'
        stmt += " }"
        return stmt