import { Component, OnInit, Directive, Input, Output, EventEmitter, ViewChildren, QueryList } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AssociationService } from '../association.service';
import { _ } from 'underscore';
import { LookupService } from '../lookup.service';
import { NgbNavChangeEvent, NgbAlertConfig, NgbModal } from '@ng-bootstrap/ng-bootstrap';


export type SortColumn = 'conceptLabel' | 'val' | '';
export type SortDirection = 'asc' | 'desc' | '';
const rotate: {[key: string]: SortDirection} = { 'asc': 'desc', 'desc': '', '': 'asc' };


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
  conceptRedirect = "association";
  associations = null;
  types = [];
  active = 1;
  query='';
  endpoint='';
  annontationQuery='';
  similarityQuery='';
  geneValuesets = [];
  showTypeFilter = true;


  currentJustify = 'start';

  BASE_PREFIX = "http://phenomebrowser.net/"
  tabId = 0;

  constructor(
    private router: Router,
    private route: ActivatedRoute, 
    private associationService: AssociationService,
    private lookupService: LookupService,
    private alertConfig: NgbAlertConfig,
    private modalService: NgbModal) { 
      alertConfig.type = 'secondary';
      this.route.params.subscribe( params => {
        this.iri = decodeURIComponent(params.iri);
        this.valueset = params.valueset ? params.valueset : ''
        if (this.iri && this.valueset) {
          this.active=1;
          this.initAssociation()
        }
      });
      this.geneValuesets = lookupService.GENE_VALUESETS;
  }

  ngOnInit() {
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

  onSimilarQueryChange(query) {
    if (query) {
      this.similarityQuery = query;
    }
  }

  openInNewTab(url: string) {
    window.open(url, "_blank");
  }

  initAssociation() {
    this.entities = {};
    this.similarEntities = {};
    if (this.valueset == 'MP' || this.valueset == 'HP') {
      var i = 0
      this.types = [];
      for (var key in this.associationService.TYPES) {
        if (key == 'Phenotype') 
          continue
        this.types[i] = this.associationService.TYPES[key];
        i++;
      }
    } else {
      this.types = [this.associationService.TYPES['Phenotype']]
    }
    this.resolveEntities(null);
  }

  resolveEntities(associations){
    var entityIris = new Set() 
    entityIris.add(this.iri)

    // var concepts = _.map(associations, (obj) => obj['concept']['value'])
    // concepts.forEach(item => entityIris.add(item))
    // var phenotype = _.map(associations, (obj) => obj['phenotype']['value'])
    // phenotype.forEach(item => entityIris.add(item))
    // var phenotype = _.map(associations, (obj) => obj['evidence']['value'])
    // phenotype.forEach(item => entityIris.add(item))

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

  onNavChange(changeEvent: NgbNavChangeEvent) {
    this.tabId = changeEvent.nextId;
    if (changeEvent.nextId === this.types.length + 1) {
      this.query = this.similarityQuery;
    } else {
      this.query = this.annontationQuery;
    }
  }

  open(url) {
    this.router.navigate([url]);
  }
}
