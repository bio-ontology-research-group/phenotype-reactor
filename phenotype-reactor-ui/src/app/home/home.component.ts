import { Component, OnInit, Directive, Input, Output, EventEmitter, ViewChildren, QueryList } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AssociationService } from '../association.service';
import { _ } from 'underscore';
import { LookupService } from '../lookup.service';
import { NgbNavChangeEvent, NgbAlertConfig, NgbModal } from '@ng-bootstrap/ng-bootstrap';


export type SortColumn = 'conceptLabel' | 'val' | '';
export type SortDirection = 'asc' | 'desc' | '';
const rotate: {[key: string]: SortDirection} = { 'asc': 'desc', 'desc': '', '': 'asc' };

export interface SortEvent {
  column: SortColumn;
  direction: SortDirection;
}

@Directive({
  selector: 'th[sortable]',
  host: {
    '[class.asc]': 'direction === "asc"',
    '[class.desc]': 'direction === "desc"',
    '(click)': 'rotate()'
  }
})
export class ListSimilarEntitiesSortableHeader {

  @Input() sortable: SortColumn = '';
  @Input() direction: SortDirection = '';
  @Output() sort = new EventEmitter<SortEvent>();

  rotate() {
    this.direction = rotate[this.direction];
    this.sort.emit({column: this.sortable, direction: this.direction});
  }
}

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {

  @ViewChildren(ListSimilarEntitiesSortableHeader) headers: QueryList<ListSimilarEntitiesSortableHeader>;

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
  query='';
  annontationQuery='';
  similarityQuery='';
  typeFilter='';
  mostSimilarQueryOrderBy = '';
  popSimilarEntity = null;
  commonPhenotypes = [];
  geneValuesets = [];


  page = 1;
  pageSize = 20;
  collectionSize = 0

  currentJustify = 'start';

  BASE_PREFIX = "http://phenomebrowser.net/"
  TYPES = [];
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
          this.initAssociation()
        }
      });
      this.geneValuesets = lookupService.GENE_VALUESETS;
  }

  ngOnInit() {
    this.collectionSize = this.mostSimilarConcepts ? this.mostSimilarConcepts.length : 0;

    for (var key in this.associationService.TYPES) {
      this.TYPES.push(this.associationService.TYPES[key])
    }
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
    this.findMostSimilar();
    this.resolveEntities(null);
  }

  onTypeSelect(event) {
    this.similarEntities = {};
    this.page = 1;
    this.typeFilter = event.target.value;
    this.findMostSimilar();
  }

  // resolveSimilarEntities(associations) {
  //   var entityIris = new Set() 
  //   var concepts = _.map(associations, (obj) => obj['concept']['value'])
  //   concepts.forEach(item => entityIris.add(item))

  //   var iris = Array.from(entityIris.values());

  //   this.lookupService.findEntityByIris(iris, data => {
  //     var tmp = {};
  //     if (data) {
  //       (data as []).forEach((obj) => tmp[obj['entity']]=  obj)
  //       for (let uri in tmp) {
  //         this.similarEntities[uri] = tmp[uri]
  //       }
  //     }
  //   });
  // }

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

  sortType(types){
    return types.sort((one, two) => (one.replace(this.BASE_PREFIX, "") < two.replace(this.BASE_PREFIX, "")) ? -1 : 1);
  }

  get similarConceptsPage() {
    this.collectionSize = this.mostSimilarConcepts ? this.mostSimilarConcepts.length : 0;
    var similarConceptsPage =  this.mostSimilarConcepts ? this.mostSimilarConcepts
      .map((concept, i) => ({id: i + 1, ...concept}))
      .slice((this.page - 1) * this.pageSize, (this.page - 1) * this.pageSize + this.pageSize) : []; 
    
    return similarConceptsPage;
  }

  onSort({column, direction}: SortEvent) {
    // resetting other headers
    this.headers.forEach(header => {
      if (header.sortable !== column) {
        header.direction = '';
      }
    });

    if (direction === '' || column === '') {
      this.mostSimilarQueryOrderBy = '';
    } else {
      this.mostSimilarQueryOrderBy = direction + ":" + column;
    }
    this.findMostSimilar();
  }
  
  findMostSimilar() {
    this.associationService.findMostSimilar(this.iri, this.typeFilter, this.mostSimilarQueryOrderBy).subscribe( data => {
      this.mostSimilarConcepts = data ? data['results']['bindings'] : [];
      this.similarityQuery = data ? data['query'] : '';
      this.query = this.similarityQuery;
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

  openConcept(concept) {
    var valueset = this.lookupService.findValuesetName(concept)
    this.router.navigate(['/association', concept, valueset]);
  }

  displayConcept(concept) {
    var iris = [concept]
    this.popSimilarEntity = null;
    this.lookupService.findEntityByIris(iris, data => {
      this.popSimilarEntity = data[0]
    });
  }

  index(i: number, obj: any) {
    return i;
  }

  openCommonPhenotypeModel(target, content) {
    this.associationService.findCommonPhenotypes(this.entity.entity, target).subscribe( data => {
      this.commonPhenotypes = data ? data['results']['bindings'] : [];
      this.modalService.open(content, { size: 'lg' });
    });
  }

}
