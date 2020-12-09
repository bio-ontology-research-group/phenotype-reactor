import { Component, OnInit, Input, Directive, Output, EventEmitter, ViewChildren, QueryList, SimpleChange } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbAlertConfig } from '@ng-bootstrap/ng-bootstrap';
import { AssociationService } from '../association.service';
import { LookupService } from '../lookup.service';
import { _ } from 'underscore';

export type SortColumn = 'name' | 'evidenceLabel' | 'created' | '';
export type SortDirection = 'asc' | 'desc' | '';
const rotate: {[key: string]: SortDirection} = { 'asc': 'desc', 'desc': '', '': 'asc' };

const compare = (v1: string | number, v2: string | number) => v1 < v2 ? -1 : v1 > v2 ? 1 : 0;

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
export class ListAssoicationSortableHeader {

  @Input() sortable: SortColumn = '';
  @Input() direction: SortDirection = '';
  @Output() sort = new EventEmitter<SortEvent>();

  rotate() {
    this.direction = rotate[this.direction];
    this.sort.emit({column: this.sortable, direction: this.direction});
  }
}

@Component({
  selector: 'app-list-association',
  templateUrl: './list-association.component.html',
  styleUrls: ['./list-association.component.css'],
  providers: [NgbAlertConfig]
})
export class ListAssociationComponent implements OnInit {

  @Input() iri = null;
  @Input() type = null;
  @Input() mostSimilarConcepts = [];
  @Input() similarEntities = {};
  @Input() valueset = {};
  @Input() valuesetList = [];
  @Output() annontationQuery = new EventEmitter<any>();

  @ViewChildren(ListAssoicationSortableHeader) headers: QueryList<ListAssoicationSortableHeader>;

  page = 1;
  previousPage = 1;
  pageSize = 20;
  collectionSize = 0;
  associations = [];
  entities = {};
  orderBy = '';
  EVIDENCE : any = [];
  evidenceFilter = '';
  associationsetFilter = '';
  popEntity = null;
  geneValuesets=[]
  associationsets : any = []
  associationsetsFiltered : any = []
  valuesetEntityType = '';

  BASE_PREFIX = "http://phenomebrowser.net/"

  constructor(private router: Router,
    private route: ActivatedRoute, 
    private associationService: AssociationService,
    private alertConfig: NgbAlertConfig,
    private lookupService: LookupService) { 
    alertConfig.type = 'secondary';
    this.geneValuesets = lookupService.GENE_VALUESETS;
    for (var key in this.associationService.EVIDENCE) {
      this.EVIDENCE.push(this.associationService.EVIDENCE[key])
    }

    this.associationService.findAssociationset().subscribe(res => {
      this.associationsets = res['results']['bindings'];
      if (this.type.name != 'Phenotype') {
        this.associationsetsFiltered = _.filter(this.associationsets, (obj) => obj['type']['value'] == this.type.uri);
      } else {
        if (this.valuesetList) {
          this.valuesetEntityType = _.filter(this.valuesetList, (obj) => obj.valueset == this.valueset)[0].entity_type;
          this.associationsetsFiltered = _.filter(this.associationsets, (obj) => obj['type']['value'] == this.BASE_PREFIX + this.valuesetEntityType);
        }
      }
      this.sortAssociationset(this.associationsetsFiltered)
    })
  }

  ngOnInit() {

  }

  ngOnChanges(change: SimpleChange) {
    if(change && change['iri'] && this.iri) {
      this.page = 1;
      this.previousPage = 1;
      this.pageSize = 20;
      this.getPage();
      if (this.valuesetList) {
        this.valuesetEntityType = _.filter(this.valuesetList, (obj) => obj.valueset == this.valueset)[0].entity_type;
        this.associationsetsFiltered = _.filter(this.associationsets, (obj) => obj['type']['value'] == this.BASE_PREFIX + this.valuesetEntityType);
      }
    }
  }

  onEvidenceSelect(event) {
    this.similarEntities = {};
    this.page = 1;
    this.evidenceFilter = event.target.value;
    this.getPage();
  }

  onDatasetSelect(event) {
    this.similarEntities = {};
    this.page = 1;
    this.associationsetFilter = event.target.value;
    this.getPage();
  }

  getPage() {
    if (this.iri && this.type) { 
      var findAssociation = null;
      var offset = 1
      if (this.page > 1) {
        offset = this.pageSize * (this.page - 1)
      }

      if (this.type.name == 'Phenotype') {
        findAssociation = this.associationService.find(this.iri, null, null, this.evidenceFilter, this.associationsetFilter, this.pageSize, offset, this.orderBy)
      } else {
        findAssociation = this.associationService.find(null, this.iri, this.type.uri, this.evidenceFilter, this.associationsetFilter, this.pageSize, offset, this.orderBy)
      }
      
      findAssociation.subscribe(data => {
        let result = data ? data['results']['bindings'] : [];
        this.associations = result.length > 1 ? result.slice(0,result.length - 1): []; 
        this.annontationQuery.emit(data ? data['query'] : '')
        this.collectionSize = result.length > 1 ? result[result.length - 1]['total']['value'] : 0;
      })
    }
  }


  loadPage(page: number) {
    if (page !== this.previousPage) {
      this.previousPage = page;
      this.getPage()
    }
  }

  onPageSizeChange(event){
    this.getPage();
  }

  onSort({column, direction}: SortEvent) {
    // resetting other headers
    console.log(column, direction)
    this.headers.forEach(header => {
      if (header.sortable !== column) {
        header.direction = '';
      }
    });

    // sorting countries
    if (direction === '' || column === '') {
      this.orderBy = '';
    } else {
      this.orderBy = direction + ":";
      if (this.type.name == "Phenotype" &&  column == "name") {
        this.orderBy += "phenotypeLabel";
      } else if (column == "name") {
        this.orderBy += "conceptLabel";
      } else {
        this.orderBy += column;
      }
    }
    this.getPage()
  }

  openInNewTab(url: string) {
    window.open(url, "_blank");
  }

  open(concept) {
    var valueset = this.lookupService.findValuesetName(concept)
    this.router.navigate(['/association', concept, valueset]);
  }

  displayConcept(concept) {
    var iris = [concept]
    this.popEntity = null;
    this.lookupService.findEntityByIris(iris, data => {
      this.popEntity = data[0]
    });
  }


  sortAssociationset(lookupList) {
    return lookupList.sort((one, two) => (one.label.value  < two.label.value ? -1 : 1));
  }
}
