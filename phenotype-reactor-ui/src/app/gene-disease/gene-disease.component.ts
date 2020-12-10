import { TitleCasePipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { LookupService } from '../lookup.service';
import { Observable, of, Subject, merge } from 'rxjs';
import {debounceTime, distinctUntilChanged, tap, switchMap, catchError} from 'rxjs/operators';
import { _ } from 'underscore';

@Component({
  selector: 'app-gene-disease',
  templateUrl: './gene-disease.component.html',
  styleUrls: ['./gene-disease.component.css']
})
export class GeneDiseaseComponent implements OnInit {

  BASE_PREFIX = "http://phenomebrowser.net/"
  focus$ = new Subject<string>();

  selectedType = 'Gene'
  types = ['Gene', 'Disease']
  targetType = null;
  typesDisplay = {'Gene' : 'Gene by Symbol or Name', 'Disease' : 'Disease Name'};
  term = null;
  searching = false;
  searchFailed = false;
  valuesets : any = [];
  selectedValuesets : any = [];
  geneValuesets = [];

  iri = null;
  valueset = null;
  entity = null;

  active = 1;
  similarEntityTypes = [this.BASE_PREFIX + this.types[0], this.BASE_PREFIX + this.types[1]];

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

  constructor(private lookupService: LookupService,
    private router: Router,
    private route: ActivatedRoute, 
    private titlecasePipe:TitleCasePipe,
    private modalService: NgbModal) { 
      this.route.params.subscribe( params => {
        this.iri = decodeURIComponent(params.iri);
        this.valueset = params.valueset ? params.valueset : ''
        if (params.iri && params.valueset) {
          this.active = 1;
          if (this.valuesets && this.valuesets.length > 0) {
            this.selectedType = _.filter(this.valuesets, (obj) => obj.valueset == this.valueset)[0].entity_type;
          }
          this.updateTargetType();
          this.resolveEntity();
        }
      });
      this.geneValuesets = lookupService.GENE_VALUESETS;
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
      this.entity = event.item 
      this.router.navigate(['/genedisease', encodeURIComponent(event.item.entity), event.item.valueset]);
    }
  }

  onTypeSelect(event) {
    this.selectedType = event.target.value;
    this.selectedValuesets = _.map(_.filter(this.valuesets, (obj) => obj.entity_type == this.selectedType), obj => obj.valueset);
    this.updateTargetType();
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

  sortType(types){
    return types.sort((one, two) => (one.replace(this.BASE_PREFIX, "") < two.replace(this.BASE_PREFIX, "")) ? -1 : 1);
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

  onQueryChange(query) {
    // if (query) {
    //   this.query = query;
    // }
  }

  openGeneDisease(concept) {
    var valueset = this.lookupService.findValuesetName(concept)
    this.modalService.dismissAll();
    this.router.navigate(['/genedisease', concept, valueset]);
  }

  openHelp(content) {
    this.modalService.open(content, { size: 'lg' });
  }

  updateTargetType(){
    this.targetType = this.BASE_PREFIX;
    if (this.selectedType == this.types[0]) {
      this.targetType = this.targetType + this.types[1]
    } else {
      this.targetType = this.targetType + this.types[0]
    }
  }
}
