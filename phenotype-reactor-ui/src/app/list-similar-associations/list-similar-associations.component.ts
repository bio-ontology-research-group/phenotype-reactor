import { Component, OnInit, Directive, Input, Output, EventEmitter, ViewChildren, QueryList, SimpleChange } from '@angular/core';
import { Subject} from 'rxjs';
import { startWith, map } from 'rxjs/operators';
import { FormControl } from '@angular/forms';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ActivatedRoute, Router } from '@angular/router';
import { LookupService } from '../lookup.service';
import { AssociationService } from '../association.service';

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
@Component({
  selector: 'app-list-similar-associations',
  templateUrl: './list-similar-associations.component.html',
  styleUrls: ['./list-similar-associations.component.css']
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

const compare = (v1: string | number, v2: string | number) => v1 < v2 ? -1 : v1 > v2 ? 1 : 0;

@Component({
  selector: 'app-list-similar-associations',
  templateUrl: './list-similar-associations.component.html',
  styleUrls: ['./list-similar-associations.component.css']
})
export class ListSimilarAssociationsComponent implements OnInit {
  @ViewChildren(ListSimilarEntitiesSortableHeader) headers: QueryList<ListSimilarEntitiesSortableHeader>;
  focus$ = new Subject<string>();

  @Output() similarityQuery = new EventEmitter<any>();

  @Input() iri = null;
  @Input() valueset = null;
  @Input() selectedType = null;
  @Input() targetType = null;
  @Input() conceptRedirect = null;
  @Input() showTypeFilter = false;

  mostSimilarConcepts : any = [];
  mostSimilarConceptsPlusSelectedEntity : any = [];
  mostSimilarConceptsFiltered : any = [];
  mostSimilarQueryOrderBy = 'desc:val';
  conceptPhenotypesMap = {};
  conceptSuperclassPhenotypesMap = {};
  query = '';
  typeFilter = '';
  TYPES = [];

  filter = new FormControl('');

  page = 1;
  pageSize = 20;
  collectionSize = 0;

  popSimilarEntity = null;
  associationLoading = false;

  conceptfilter = (text: string): [] => {
    return this.mostSimilarConcepts.filter(concept => {
      const term = text.toLowerCase();
      if (concept.conceptLabel) {
        return concept.conceptLabel.value.toLowerCase().includes(term);
      } else {
        return false;
      }
    });
  }
  
  constructor(private lookupService: LookupService,
    private router: Router,
    private associationService: AssociationService) {
    this.filter.valueChanges.pipe(
      startWith(''),
      map(text => this.conceptfilter(text))
    ).subscribe(data => {this.mostSimilarConceptsFiltered = data;});
    for (var key in this.associationService.TYPES) {
      this.TYPES.push(this.associationService.TYPES[key])
    }
  }

  ngOnInit() {
  }

  ngOnChanges(change: SimpleChange) {
    if((change && this.iri && (this.targetType != undefined || this.targetType != null))) {
      this.conceptPhenotypesMap = {};
      this.findMostSimilar();
    } 
  }


  get similarConceptsPage() {
    this.associationLoading = true;
    this.collectionSize = this.mostSimilarConceptsFiltered ? this.mostSimilarConceptsFiltered.length : 0;
    var similarConceptsPage =  this.mostSimilarConceptsFiltered ? this.mostSimilarConceptsFiltered
      .map((concept, i) => ({id: i + 1, ...concept}))
      .slice((this.page - 1) * this.pageSize, (this.page - 1) * this.pageSize + this.pageSize) : []; 
    this.associationLoading = false;
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
      this.mostSimilarConceptsFiltered = this.conceptfilter(this.filter.value);
    } else {
      this.mostSimilarConceptsFiltered = this.mostSimilarConceptsFiltered.sort((a, b) => {
        const res = compare(a[column]['value'], b[column]['value']);
        return direction === 'asc' ? res : -res;
      });
    }
  }

  conceptRef(concept) {
    var valueset = this.lookupService.findValuesetName(concept)
    return `/association/${encodeURIComponent(concept)}/${valueset}`;
  }

  conceptRedirectRef(concept) {
    var valueset = this.lookupService.findValuesetName(concept)
    return `/${this.conceptRedirect}/${encodeURIComponent(concept)}/${valueset}`;
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

  findMostSimilar() {
    this.associationLoading = true;
    var type;
    if (this.showTypeFilter) {
      type = this.typeFilter;
    } else {
      type = this.targetType;
    }


    this.filter.setValue('')
    this.associationService.findMostSimilar(this.iri, type, this.mostSimilarQueryOrderBy, null).subscribe( data => {
      this.mostSimilarConcepts = data ? data['results']['bindings'] : [];
      this.mostSimilarConceptsPlusSelectedEntity = Object.assign([], this.mostSimilarConcepts);
      this.similarityQuery.emit(data ? data['query'] : '')
      this.mostSimilarConceptsFiltered = this.conceptfilter(this.filter.value);

      if (!['HP','MP'].includes(this.valueset)) {
        this.mostSimilarConcepts.forEach(concept => {
          if (concept.type.value == this.associationService.TYPES['Phenotype'].uri) {
            return;
          }
          this.associationService.findMatchingPhenotypes(this.iri, concept.concept.value).subscribe( data => {
            this.conceptPhenotypesMap[this.iri + '|' + concept.concept.value] = data ? data['results']['bindings'] : [];
            if (this.conceptPhenotypesMap[this.iri + '|' + concept.concept.value].length < 1) {
              this.associationService.findMatchingPhenotypeSuperClasses(this.iri, concept.concept.value).subscribe( data => {
                this.conceptSuperclassPhenotypesMap[this.iri + '|' + concept.concept.value] = data ? this.sortAberowlClasses(data) : [];
              });
            }
          })
        });
      }

      this.associationLoading = false;
      // To get coordinates of entity selected
      this.associationService.findMostSimilar(this.iri, '', this.mostSimilarQueryOrderBy, 1).subscribe( data => {
        var selectedEntityCoordinates = data ? data['results']['bindings'][0] : null;
        if (selectedEntityCoordinates) {
          this.mostSimilarConceptsPlusSelectedEntity = this.mostSimilarConceptsPlusSelectedEntity.concat([selectedEntityCoordinates]);
        }
      });
    });

  }


  onTypeSelect(event) {
    this.typeFilter = event.target.value;
    this.findMostSimilar();
  }

  sortAberowlClasses(classes) {
    return classes.sort((one, two) => (one.label < two.label ? -1 : 1));
  }

}
