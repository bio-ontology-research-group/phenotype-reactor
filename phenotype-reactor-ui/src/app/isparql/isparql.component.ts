import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-isparql',
  templateUrl: './isparql.component.html',
  styleUrls: ['./isparql.component.css']
})
export class ISparqlComponent implements OnInit {

  formats = [
    {name: 'HTML',  format:'text/html'},
    {name: 'XML',  format:'application/sparql-results+xml'},
    {name: 'JSON',  format:'application/sparql-results+json'},
    {name: 'Javascript',  format:'application/javascript'},
    {name: 'Turtle',  format:'text/turtle'},
    {name: 'RDF/XML',  format:'application/rdf+xml'},
    {name: 'N-Triples',  format:'text/plain'},
    {name: 'CSV',  format:'text/csv'},
    {name: 'TSV',  format:'text/tab-separated-values'}
  ];

  format: any = {name: 'HTML',  format:'text/html'};
  @ViewChild("htmlForm", {static: false})
  htmlForm: ElementRef;
  @ViewChild("sparqlEle", {static: false})
  sparqlEle: ElementRef;
  
  query = '';

  constructor(private http: HttpClient) { }

  ngOnInit() {
    this.listConceptsByPhenotype()
  }

  submit(){
    this.htmlForm.nativeElement.submit();
  }

  clear(){
    this.query = '';
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
    ?association rdf:object obo:HP_0002938 .
    ?association rdf:subject ?concept .
    ?association dc:provenance ?prov .
    ?prov dc:creator ?creator .
    ?prov dcterms:source ?source .
}`;
    this.query = query;
  }
}
