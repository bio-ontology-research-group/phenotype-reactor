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

  constructor() { }

  ngOnInit() {
  }

  submit(){
    this.htmlForm.nativeElement.submit();
  }

  clear(){
    this.query = '';
  }
}
