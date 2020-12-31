import { Component, OnInit} from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-isparql',
  templateUrl: './isparql.component.html',
  styleUrls: ['./isparql.component.css']
})
export class ISparqlComponent implements OnInit {
  
  query = '';

  constructor(private http: HttpClient) { }

  ngOnInit() {
    this.listConceptsByPhenotype()
  }

  listConceptsByPhenotype() {
    var query = `PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX pb: <http://phenomebrowser.net/>
PREFIX obo: <http://purl.obolibrary.org/obo/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
     
SELECT ?association ?concept ?creator ?source
FROM <http://phenomebrowser.net>
WHERE {
    ?association rdf:type rdf:Statement .
    ?association rdf:predicate obo:RO_0002200 .
    ?association rdf:object obo:HP_0031246 .
    ?association rdf:subject ?concept .
    ?association dc:provenance ?prov .
    ?prov dc:creator ?creator .
    ?prov dcterms:source ?source .
}`;
    this.query = query;
  }

  listMostSimilarToAcuteDiarrhea() {
    var query = `PREFIX b2v: <http://bio2vec.net/function#>
PREFIX b2vd: <http://bio2vec.net/dataset#>

SELECT ?sim ?simLabel ?type ?val ?x ?y
WHERE {
  SERVICE <https://bio2vec.cbrc.kaust.edu.sa/ds/query> { 
      (?sim ?val ?x ?y) b2v:mostSimilar(b2vd:dataset_4 <http://purl.obolibrary.org/obo/MONDO_0000257> 10) . 
  } 
  GRAPH <http://phenomebrowser.net> {
    ?sim a ?type .
    OPTIONAL { ?sim rdfs:label ?simLabel } .
  }
}`;
    this.query = query;
  }

  listMostSimilarDiseaseToCardiacArrest() {
  var query = `PREFIX b2v: <http://bio2vec.net/function#>
PREFIX b2vd: <http://bio2vec.net/dataset#>

SELECT ?sim ?simLabel ?type ?val ?x ?y
WHERE {
SERVICE <https://bio2vec.cbrc.kaust.edu.sa/ds/query> { 
    (?sim ?val ?x ?y) b2v:mostSimilar(b2vd:dataset_4 <http://purl.obolibrary.org/obo/DOID_0060319> 10 <http://phenomebrowser.net/Disease>) . 
} 
GRAPH <http://phenomebrowser.net> {
  ?sim a ?type .
  OPTIONAL { ?sim rdfs:label ?simLabel } .
}
}`;
    this.query = query;
  }

  listMatchingPhenotypes() {
    var query = `PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
  PREFIX pb: <http://phenomebrowser.net/> 
  PREFIX obo: <http://purl.obolibrary.org/obo/> 
  
  SELECT ?phenotype ?phenotypeLabel 
  FROM <http://phenomebrowser.net> 
  WHERE { 
    <http://purl.obolibrary.org/obo/NCBITaxon_64320> obo:RO_0002200 ?phenotype . 
    <https://www.ncbi.nlm.nih.gov/gene/6773> obo:RO_0002200 ?phenotype . 
    ?phenotype rdfs:label ?phenotypeLabel . 
  } ORDER BY asc(?phenotypeLabel)`;
    this.query = query;
  }

  listAllPhenotypes() {
    var query = `PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
  PREFIX pb: <http://phenomebrowser.net/> 
  PREFIX obo: <http://purl.obolibrary.org/obo/> 
  
  SELECT ?phenotype ?phenotypeLabel 
  FROM <http://phenomebrowser.net> 
  WHERE { 
    <http://purl.obolibrary.org/obo/DOID_1307> obo:RO_0002200 ?phenotype . 
    ?phenotype rdfs:label ?phenotypeLabel . 
  } ORDER BY asc(?phenotypeLabel)`;
    this.query = query;
  }
}
