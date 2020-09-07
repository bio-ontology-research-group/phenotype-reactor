import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AssociationService } from '../association.service';
import { _ } from 'underscore';
import { LookupService } from '../lookup.service';
import { NgbNavChangeEvent, NgbAlertConfig } from '@ng-bootstrap/ng-bootstrap';

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
  valueset = '';
  associations = null;
  mostSimilarConcepts = null
  typeToAssoicationMap = {};
  types = [];
  active = 1;
  query=''
  annontationQuery=''
  similarityQuery=''
  typeFilter=''


  page = 1;
  pageSize = 20;
  collectionSize = 0

  currentJustify = 'start';

  BASE_PREFIX = "http://phenomebrowser.net/"
  PUBMED_PREFIX = "http://phenomebrowser.net/"
  TYPES = [];
  tabId = 0;

  constructor(
    private router: Router,
    private route: ActivatedRoute, 
    private associationService: AssociationService,
    private lookupService: LookupService,
    private alertConfig: NgbAlertConfig) { 
      alertConfig.type = 'secondary';
      this.route.params.subscribe( params => {
        this.iri = decodeURIComponent(params.iri);
        this.valueset = params.valueset ? params.valueset : ''
        if (this.iri && this.valueset) {
          this.initAssociation()
        }
      });
  }

  ngOnInit() {
    this.collectionSize = this.mostSimilarConcepts ? this.mostSimilarConcepts.length : 0;
  }

  onTermSelect(lookupResource) {
    if (lookupResource && lookupResource.valueset) {
      this.entity = lookupResource
      this.router.navigate(['/association', encodeURIComponent(lookupResource.entity), lookupResource.valueset]);
    }
  }

  onQueryChange(query) {
    if (query) {
      this.query = query;
    }
  }

  openInNewTab(url: string) {
    window.open(url, "_blank");
  }

  initAssociation() {
    this.entities = {};
    this.similarEntities = {};
    if (this.valueset == 'MP' || this.valueset == 'HP') {
      // this.associationService.find(null, this.iri, null, null, null).subscribe( data => {
      //   this.associations = data ? data['results']['bindings'] : [];
      //   this.annontationQuery = data ? data['query'] : '';
      //   this.query = this.annontationQuery
      //   this.transformConceptAssociation(this.associations);
      //   this.resolveEntities(this.associations)
      // });
      var i = 0
      this.types = [];
      for (var key in this.associationService.TYPES) {
        if (key == 'Phenotype') 
          continue
        this.types[i] = this.associationService.TYPES[key];
        i++;
      }
    } else {
      this.associationService.find(this.iri, null, null, null, null).subscribe( data => {
        // this.associations = data ? data['results']['bindings'] : [];
        // this.annontationQuery = data ? data['query'] : '';
        // this.query = this.annontationQuery
        // this.transformPhenotypeAssociation(this.associations);
        // this.resolveEntities(this.associations)
        this.types = [this.associationService.TYPES['Phenotype']]
      });
    }
    this.associationService.findMostSimilar(this.iri, this.typeFilter).subscribe( data => {
      this.mostSimilarConcepts = data ? data['results']['bindings'] : [];
      this.similarityQuery = data ? data['query'] : '';
      this.resolveSimilarEntities(this.mostSimilarConcepts)
    });
  }

  onTypeSelect(event) {
    this.similarEntities = {};
    this.page = 1;
    this.typeFilter = event.target.value;
    this.associationService.findMostSimilar(this.iri, this.typeFilter).subscribe( data => {
      this.mostSimilarConcepts = data ? data['results']['bindings'] : [];
      this.similarityQuery = data ? data['query'] : '';
      this.query = this.similarityQuery;
      this.resolveSimilarEntities(this.mostSimilarConcepts)
    });
  }

  resolveSimilarEntities(associations) {
    var entityIris = new Set() 
    var concepts = _.map(associations, (obj) => obj['concept']['value'])
    concepts.forEach(item => entityIris.add(item))

    var iris = Array.from(entityIris.values());

    this.lookupService.findEntityByIris(iris, data => {
      var tmp = {};
      if (data) {
        (data as []).forEach((obj) => tmp[obj['entity']]=  obj)
        for (let uri in tmp) {
          this.similarEntities[uri] = tmp[uri]
        }
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

    this.lookupService.findEntityByIris(iris, data => {
      var tmp = {};
      if (data) {
        (data as []).forEach((obj) => tmp[obj['entity']]=  obj)
        for (let uri in tmp) {
          this.entities[uri] = tmp[uri]
        }
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
    this.collectionSize = this.mostSimilarConcepts ? this.mostSimilarConcepts.length : 0;
    return this.mostSimilarConcepts ? this.mostSimilarConcepts
      .map((concept, i) => ({id: i + 1, ...concept}))
      .slice((this.page - 1) * this.pageSize, (this.page - 1) * this.pageSize + this.pageSize) : []; 
  }

  onNavChange(changeEvent: NgbNavChangeEvent) {
    this.tabId = changeEvent.nextId;
    if (changeEvent.nextId === this.types.length + 1) {
      this.query = this.similarityQuery;
    } else {
      this.query = this.annontationQuery;
    }
  }

}
