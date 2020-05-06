import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AssociationService } from '../association.service';
import { _ } from 'underscore';
import { LookupService } from '../lookup.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {

  entity = null;
  iri = null;
  valueset = null;
  associations = null;
  valuesetToAssoicationMap = {};

  currentJustify = 'start';

  BASE_PREFIX = "http://phenomebrowser.net/"


  constructor(
    private router: Router,
    private route: ActivatedRoute, 
    private associationService: AssociationService) { 
      this.route.params.subscribe( params => {
        this.iri = decodeURIComponent(params.iri);
        this.valueset = params.valueset
        if (this.iri && this.valueset) {
          this.initAssociation()
        }
      });
  }

  ngOnInit() {
  }

  onTermSelect(lookupResource) {
    if (lookupResource && lookupResource.valueset) {
      this.entity = lookupResource
      console.log(this.entity)
      this.router.navigate(['/association', encodeURIComponent(lookupResource.entity), lookupResource.valueset]);
    }
  }

  openInNewTab(url: string) {
    window.open(url, "_blank");
  }

  initAssociation() {
    if (this.valueset == 'MP' || this.valueset == 'HP') {
      this.associationService.find(null, this.iri, null).subscribe( data => {
        this.associations = data ? data['results']['bindings'] : [];
        this.transformAssociation(this.associations);
      });
    } else {
      this.associationService.find(this.iri, null, null).subscribe( data => {
        this.associations = data ? data['results']['bindings'] : [];
        this.transformAssociation(this.associations);
      });
    }
  }

  transformAssociation(associations) {
    this.valuesetToAssoicationMap = {};
    var types = _.map(associations, (obj) => obj['conceptType']['value'])
    for (var index in types) {
      this.valuesetToAssoicationMap[types[index]] = _.filter(associations, (obj) => obj['conceptType']['value'] == types[index]);
    }
    console.log(this.valuesetToAssoicationMap)
  }

}
