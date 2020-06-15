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
  entities = {};
  similarEntities = {}
  iri = null;
  valueset = 'HP';
  associations = null;
  mostSimilarConcepts = null
  typeToAssoicationMap = {};
  types = [];
  active = 1;

  page = 1;
  pageSize = 20;
  collectionSize = 0

  currentJustify = 'start';

  BASE_PREFIX = "http://phenomebrowser.net/"
  PUBMED_PREFIX = "http://phenomebrowser.net/"


  constructor(
    private router: Router,
    private route: ActivatedRoute, 
    private associationService: AssociationService,
    private lookupService: LookupService) { 
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
        this.transformConceptAssociation(this.associations);
        this.resolveEntities(this.associations)
      });
    } else {
      this.associationService.find(this.iri, null, null).subscribe( data => {
        this.associations = data ? data['results']['bindings'] : [];
        this.transformPhenotypeAssociation(this.associations);
        this.resolveEntities(this.associations)
      });
    }
    this.associationService.findMostSimilar(this.iri).subscribe( data => {
      this.mostSimilarConcepts = data ? data['results']['bindings'] : [];
      this.resolveSimilarEntities(this.mostSimilarConcepts)
    });
  }

  resolveSimilarEntities(associations){
    var entityIris = new Set() 
    var concepts = _.map(associations, (obj) => obj['concept']['value'])
    concepts.forEach(item => entityIris.add(item))

    var iris = Array.from(entityIris.values());

    this.lookupService.findEntityByIris(iris).subscribe( data => {
      var tmp = {};
      if (data) {
        (data as []).forEach((obj) => tmp[obj['entity']]=  obj)
        this.similarEntities = tmp
      }
    });
  }

  resolveEntities(associations){
    var entityIris = new Set() 
    entityIris.add(this.iri)

    var concepts = _.map(associations, (obj) => obj['concept']['value'])
    concepts.forEach(item => entityIris.add(item))
    var phenotype = _.map(associations, (obj) => obj['phenotype']['value'])
    phenotype.forEach(item => entityIris.add(item))
    var phenotype = _.map(associations, (obj) => obj['evidence']['value'])
    phenotype.forEach(item => entityIris.add(item))

    var iris = Array.from(entityIris.values());

    this.lookupService.findEntityByIris(iris).subscribe( data => {
      var tmp = {};
      if (data) {
        (data as []).forEach((obj) => tmp[obj['entity']]=  obj)
        this.entities = tmp
        this.entity = this.entities[this.iri]
      }
    });
  }

  transformConceptAssociation(associations) {
    this.typeToAssoicationMap = {};
    this.types = _.map(associations, (obj) => obj['conceptType']['value'])
    this.types = Array.from(new Set(this.types).values());
    for (var index in this.types) {
      this.typeToAssoicationMap[this.types[index]] = _.filter(associations, (obj) => obj['conceptType']['value'] == this.types[index]);
    }
  }

  transformPhenotypeAssociation(associations) {
    this.typeToAssoicationMap = {};
    this.types = ['Phenotype']
    this.typeToAssoicationMap[this.types[0]] = associations;
  }

  sortType(types){
    return types.sort((one, two) => (one.replace(this.BASE_PREFIX, "") < two.replace(this.BASE_PREFIX, "")) ? -1 : 1);
  }

  get similarConceptsPage(): Object[] {
    return this.mostSimilarConcepts ? this.mostSimilarConcepts
      .map((concept, i) => ({id: i + 1, ...concept}))
      .slice((this.page - 1) * this.pageSize, (this.page - 1) * this.pageSize + this.pageSize) : []; 
  }

}
