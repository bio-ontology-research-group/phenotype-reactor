import { Component, OnInit, ViewChild, ElementRef, Input  } from '@angular/core';

@Component({
  selector: 'app-sparql-form',
  templateUrl: './sparql-form.component.html',
  styleUrls: ['./sparql-form.component.css']
})
export class SparqlFormComponent implements OnInit {

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

  @Input() query = ''
  endpoint = ''

  ABEROWL_URL = "http://aber-owl.net/api/sparql"
  ABEROWL_QUERY_PATTERN = "(OWL|owl){1}[\\s]*(superclass|subclass|equivalent|supeq|subeq|realize){1}[\\s]*\\<([\\w]+:\\/\\/[\\w\\.\\/]+)>[\\s]+[\\r\\n\\s]*\\<([\\w-]*)\\>[\\s]+[\\r\\n\\s]*\\{[\\r\\n\\s]+([\\w\\s\']+)[\\r\\n\\s]+\\}[\\s]*[\\.]*"

  constructor() { }

  ngOnInit() {
  }

  submit(){
    let match = this.sparqlEle.nativeElement.value.match(this.ABEROWL_QUERY_PATTERN);
    if (match && match.length > 0) {
      this.endpoint = this.ABEROWL_QUERY_PATTERN;
    } else {
      this.endpoint = ''
    }
    this.htmlForm.nativeElement.submit();
  }

  clear(){
    this.query = '';
  }
}
