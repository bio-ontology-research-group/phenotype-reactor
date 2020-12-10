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

@Component({
  selector: 'app-list-similar-associations',
  templateUrl: './list-similar-associations.component.html',
  styleUrls: ['./list-similar-associations.component.css']
})
export class ListSimilarAssociationsComponent implements OnInit {
  @ViewChildren(ListSimilarEntitiesSortableHeader) headers: QueryList<ListSimilarEntitiesSortableHeader>;
  focus$ = new Subject<string>();

  @Input() iri = null;
  @Input() valueset = null;
  @Input() selectedType = null;
  @Input() targetType = null;

  mostSimilarConcepts : any = [];
  mostSimilarConceptsPlusSelectedEntity : any = [];
  mostSimilarConceptsFiltered : any = [];
  mostSimilarQueryOrderBy = '';
  conceptPhenotypesMap = {};
  similarityQuery='';
  query='';

  filter = new FormControl('');

  page = 1;
  pageSize = 20;
  collectionSize = 0;

  popSimilarEntity = null;

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
  }

  ngOnInit() {
  }

  ngOnChanges(change: SimpleChange) {
    if(change && change['iri'] && this.iri) {
      this.conceptPhenotypesMap = {};
      this.findMostSimilar();
    }
  }


  get similarConceptsPage() {
    this.collectionSize = this.mostSimilarConceptsFiltered ? this.mostSimilarConceptsFiltered.length : 0;
    var similarConceptsPage =  this.mostSimilarConceptsFiltered ? this.mostSimilarConceptsFiltered
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

  conceptRef(concept) {
    var valueset = this.lookupService.findValuesetName(concept)
    return `/association/${encodeURIComponent(concept)}/${valueset}`;
  }

  geneDiseaseRef(concept) {
    var valueset = this.lookupService.findValuesetName(concept)
    return `/genedisease/${encodeURIComponent(concept)}/${valueset}`;
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
    this.associationService.findMostSimilar(this.iri, this.targetType, this.mostSimilarQueryOrderBy, null).subscribe( data => {
      this.mostSimilarConcepts = data ? data['results']['bindings'] : [];
      this.mostSimilarConceptsPlusSelectedEntity = Object.assign([], this.mostSimilarConcepts);
      this.similarityQuery = data ? data['query'] : '';
      this.query = this.similarityQuery;
      this.mostSimilarConceptsFiltered = this.conceptfilter(this.filter.value);
      this.mostSimilarConcepts.forEach(concept => {
        this.associationService.findCommonPhenotypes(this.iri, concept.concept.value).subscribe( data => {
          this.conceptPhenotypesMap[this.iri + '|' + concept.concept.value] = data ? data['results']['bindings'] : [];
        })
      });

      // To get coordinates of entity selected
      this.associationService.findMostSimilar(this.iri, '', this.mostSimilarQueryOrderBy, 1).subscribe( data => {
        var selectedEntityCoordinates = data ? data['results']['bindings'][0] : null;
        if (selectedEntityCoordinates) {
          this.mostSimilarConceptsPlusSelectedEntity = this.mostSimilarConceptsPlusSelectedEntity.concat([selectedEntityCoordinates]);
        }
      });
    });

  }

}
