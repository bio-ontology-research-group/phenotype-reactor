import { TitleCasePipe } from '@angular/common';
import { Component, OnInit, Directive, Input, Output, EventEmitter, ViewChildren, QueryList } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { LookupService } from '../lookup.service';
import { Observable, of, Subject, merge } from 'rxjs';
import {debounceTime, distinctUntilChanged, tap, switchMap, catchError, startWith, map} from 'rxjs/operators';
import { _ } from 'underscore';
import { AssociationService } from '../association.service';
import { FormControl } from '@angular/forms';

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
  selector: 'app-gene-disease',
  templateUrl: './gene-disease.component.html',
  styleUrls: ['./gene-disease.component.css']
})
export class GeneDiseaseComponent implements OnInit {
  @ViewChildren(ListSimilarEntitiesSortableHeader) headers: QueryList<ListSimilarEntitiesSortableHeader>;
  focus$ = new Subject<string>();

  selectedType = 'Gene'
  types = ['Gene', 'Disease']
  typesDisplay = {'Gene' : 'Gene by Symbol or Name', 'Disease' : 'Disease Name'};
  term = null;
  searching = false;
  searchFailed = false;
  valuesets : any = [];
  selectedValuesets : any = [];
  geneValuesets = [];
  conceptPhenotypesMap = {};
  filter = new FormControl('');

  iri = null;
  valueset = null;
  entity = null;
  similarEntityType = []

  mostSimilarConcepts : any = [];
  mostSimilarConceptsFiltered : any = [];
  mostSimilarQueryOrderBy = '';
  similarityQuery='';
  query='';
  active = 1;

  page = 1;
  pageSize = 20;
  collectionSize = 0;

  popSimilarEntity = null;

  BASE_PREFIX = "http://phenomebrowser.net/"

  formatter: any;
  
  search = (text$: Observable<string>) => {
    const debouncedText$ = text$.pipe(debounceTime(500), distinctUntilChanged());
    const inputFocus$ = this.focus$;
    return merge(debouncedText$, inputFocus$).pipe(
      switchMap(term =>
        this.findTerm(term).pipe(
          tap(() => this.searchFailed = false),
          catchError(() => {
            this.searchFailed = true;
            return of([]);
          }))
    ));
  }

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
    private route: ActivatedRoute, 
    private associationService: AssociationService,
    private titlecasePipe:TitleCasePipe,
    private modalService: NgbModal) { 
      this.route.params.subscribe( params => {
        this.iri = decodeURIComponent(params.iri);
        this.valueset = params.valueset ? params.valueset : ''
        if (this.iri && this.valueset) {
          this.active = 1;
          if (this.valuesets && this.valuesets.length > 0) {
            this.selectedType = _.filter(this.valuesets, (obj) => obj.valueset == this.valueset)[0].entity_type;
          }
          this.findMostSimilar();
          this.resolveEntity();
        }
      });
      this.geneValuesets = lookupService.GENE_VALUESETS;
      this.filter.valueChanges.pipe(
        startWith(''),
        map(text => this.conceptfilter(text))
      ).subscribe(data => {this.mostSimilarConceptsFiltered = data;});
    }

  ngOnInit() {
    this.formatter = (x: {label: { value: string}}) => x.label ? this.toTitleCase(x.label.value) : null;

    this.lookupService.findValueset().subscribe(res => {
      this.valuesets = res
      if (this.valueset) {
        this.selectedType = _.filter(this.valuesets, (obj) => obj.valueset == this.valueset)[0].entity_type;
      }
      this.selectedValuesets = _.map(_.filter(this.valuesets, (obj) => obj.entity_type == this.selectedType), obj => obj.valueset);
    })
  }

  onTermSelect(event) {
    if (event.item && event.item.valueset) {
      this.conceptPhenotypesMap = {};
      this.entity = event.item 
      this.router.navigate(['/genedisease', encodeURIComponent(event.item.entity), event.item.valueset]);
    }
  }

  onTypeSelect(event) {
    this.selectedType = event.target.value;
    this.selectedValuesets = _.map(_.filter(this.valuesets, (obj) => obj.entity_type == this.selectedType), obj => obj.valueset);
    this.conceptPhenotypesMap = {};
  }

  findTerm(term) {
      console.log('findterm', this.selectedValuesets)
      return this.lookupService.findEntityByLabelStartsWith(term, this.selectedValuesets)
  }

  sort(lookupList) {
    return lookupList.sort((one, two) => (one.name < two.name ? -1 : 1));
  }

  toTitleCase(text){
    return this.titlecasePipe.transform(text);
  }

  openInNewTab(url: string) {
    window.open(url, "_blank");
  }

  findMostSimilar() {
    var typeFilter = this.BASE_PREFIX;
    if (this.selectedType == this.types[0]) {
      typeFilter = typeFilter + this.types[1]
    } else {
      typeFilter = typeFilter + this.types[0]
    }
    this.similarEntityType = [typeFilter];

    this.associationService.findMostSimilar(this.iri, typeFilter, this.mostSimilarQueryOrderBy).subscribe( data => {
      this.mostSimilarConcepts = data ? data['results']['bindings'] : [];
      this.similarityQuery = data ? data['query'] : '';
      this.query = this.similarityQuery;
      this.mostSimilarConceptsFiltered = this.conceptfilter(this.filter.value);
      this.mostSimilarConcepts.forEach(concept => {
        this.associationService.findCommonPhenotypes(this.iri, concept.concept.value).subscribe( data => {
          this.conceptPhenotypesMap[this.iri + '|' + concept.concept.value] = data ? data['results']['bindings'] : [];
        })
      });
    });

  }

  sortType(types){
    return types.sort((one, two) => (one.replace(this.BASE_PREFIX, "") < two.replace(this.BASE_PREFIX, "")) ? -1 : 1);
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

  valusetEntityType(){
    if (this.valuesets && this.valuesets.length < 1) {
      return this.selectedType;
    }
    return _.filter(this.valuesets, (obj) => obj.valueset == this.valueset)[0].entity_type;
  }

  resolveEntity() {
    var iris = [this.iri]
    this.entity = null;
    this.lookupService.findEntityByIris(iris, data => {
      this.entity = data[0]
    });
  }

  openConcept(concept) {
    var valueset = this.lookupService.findValuesetName(concept)
    this.router.navigate(['/association', concept, valueset]);
  }

  openGeneDisease(concept) {
    var valueset = this.lookupService.findValuesetName(concept)
    this.modalService.dismissAll();
    this.router.navigate(['/genedisease', concept, valueset]);
  }

  displayConcept(concept) {
    var iris = [concept]
    this.popSimilarEntity = null;
    this.lookupService.findEntityByIris(iris, data => {
      this.popSimilarEntity = data[0]
    });
  }

  openHelp(content) {
    this.modalService.open(content, { size: 'lg' });
  }

  index(i: number, obj: any) {
    return i;
  }

  onQueryChange(query) {
    // if (query) {
    //   this.query = query;
    // }
  }
}
