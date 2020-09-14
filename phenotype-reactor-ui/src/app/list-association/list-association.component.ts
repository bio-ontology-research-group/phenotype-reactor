import { Component, OnInit, Input, Directive, Output, EventEmitter, ViewChildren, QueryList, SimpleChange } from '@angular/core';
import { NgbAlertConfig } from '@ng-bootstrap/ng-bootstrap';
import { AssociationService } from '../association.service';

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
  @Output() annontationQuery = new EventEmitter<any>();

  @ViewChildren(ListAssoicationSortableHeader) headers: QueryList<ListAssoicationSortableHeader>;

  page = 1;
  previousPage = 1;
  pageSize = 20;
  collectionSize = 0;
  associations = [];
  entities = {};
  orderBy = ''

  constructor(private associationService: AssociationService,
    private alertConfig: NgbAlertConfig) { 
    alertConfig.type = 'secondary';
  }

  ngOnInit() {
    this.getPage()
  }

  ngOnChanges(change: SimpleChange) {
    if(change && change['iri'] && this.iri) {
      console.log(this.iri, this.type)
      this.getPage();
    }
  }

  getPage() {
    if (this.iri && this.type) { 
      var findAssociation = null;
      var offset = 1
      if (this.page > 1) {
        offset = this.pageSize * (this.page - 1)
      }

      if (this.type.name == 'Phenotype') {
        findAssociation = this.associationService.find(this.iri, null, this.type.uri, this.pageSize, offset, this.orderBy)
      } else {
        findAssociation = this.associationService.find(null, this.iri, this.type.uri, this.pageSize, offset, this.orderBy)
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
}
