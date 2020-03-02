import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AssociationService } from '../association.service';
import { _ } from 'underscore';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {

  ontologyClass = null;
  iri = null;
  type = null;
  associations = null;
  typeToAssoicationMap = {};

  currentJustify = 'start';

  BASE_PREFIX = "http://phenomebrowser.net/"


  constructor(
    private router: Router,
    private route: ActivatedRoute, 
    private associationService: AssociationService) { 
      this.route.params.subscribe( params => {
        this.iri = decodeURIComponent(params.iri);
        this.type = params.type
        if (this.iri && this.type) {
          this.initAssociation()
        }
        
      });
  }

  ngOnInit() {

  }

  onTermSelect(lookupResource) {
    if (lookupResource && lookupResource.ontology) {
      this.ontologyClass = lookupResource
      console.log(this.ontologyClass)
      this.router.navigate(['/association', encodeURIComponent(lookupResource.class), lookupResource.ontology]);
    }
  }

  openInNewTab(url: string) {
    window.open(url, "_blank");
  }

  initAssociation() {
    if (this.type == 'MP' || this.type == 'HP') {
      this.associationService.find(null, this.iri, null).subscribe( data => {
        this.associations = data ? data['results']['bindings'] : [];
        this.transformAssociation(this.associations);
      });
    }
  }

  transformAssociation(associations) {
    this.typeToAssoicationMap = {};
    var types = _.map(associations, (obj) => obj['conceptType']['value'])
    for (var index in types) {
      this.typeToAssoicationMap[types[index]] = _.filter(associations, (obj) => obj['conceptType']['value'] == types[index]);
    }
    console.log(this.typeToAssoicationMap)
  }

}
