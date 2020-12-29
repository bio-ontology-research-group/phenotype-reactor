import { TitleCasePipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { LookupService } from '../lookup.service';
import { Observable, of, Subject, merge } from 'rxjs';
import {debounceTime, distinctUntilChanged, tap, switchMap, catchError} from 'rxjs/operators';
import { _ } from 'underscore';
import { AssociationService } from '../association.service';

@Component({
  selector: 'app-view-associationset',
  templateUrl: './view-associationset.component.html',
  styleUrls: ['./view-associationset.component.css']
})
export class ViewAssociationsetComponent implements OnInit {

  BASE_PREFIX = "http://phenomebrowser.net/"
  focus$ = new Subject<string>();

  selectedType = '';
  types = [];
  conceptRedirect = "associationset/"
  targetType = null;
  typesDisplay = {};
  term = null;
  searching = false;
  searchFailed = false;
  valuesets : any = [];
  selectedValuesets : any = [];
  geneValuesets = [];

  datasetId = null;
  iri = null;
  valueset = null;
  entity = null;
  query = '';
  dataset = null;
  datasetConfig = null;

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
    private associationService: AssociationService,
    private router: Router,
    private route: ActivatedRoute, 
    private titlecasePipe:TitleCasePipe,
    private modalService: NgbModal) { 
      this.route.params.subscribe( params => {
        this.datasetId = params.identifier ? params.identifier : ''
        this.iri = decodeURIComponent(params.iri);
        this.valueset = params.valueset ? params.valueset : ''

        if (params.identifier) {
          associationService.getAssociationset(this.datasetId).subscribe(res => {
            this.dataset = res['results']['bindings'] && res['results']['bindings'].length > 0 ? res['results']['bindings'][0] : null;
            associationService.getAssociationsetConfig().subscribe(res => {
              this.datasetConfig = res[this.datasetId];
              this.setSelectedValuesets();
              this.lookupService.findValueset().subscribe(res => {
                this.valuesets = res
                this.types = [];
                this.types.push(_.filter(this.valuesets, (obj) => obj.valueset.toLowerCase() == this.datasetConfig.biomedical_entity_reference_source[0].toLowerCase())[0].entity_type);
                this.types.push('Phenotype');
                this.typesDisplay = {};
                this.types.forEach(item => {
                  this.typesDisplay[item] = this.associationService.TYPES[item].display;
                });
                this.updateTargetType();
                if (!(params.iri && params.valueset)) {
                  this.selectedType = this.types[0];
                }
              });
            });

            if (params.iri && params.valueset) {
              if (this.valuesets && this.valuesets.length > 0) {
                this.selectedType = _.filter(this.valuesets, (obj) => obj.valueset.toLowerCase() == this.valueset.toLowerCase())[0].entity_type;
                this.setSelectedValuesets();
                this.updateTargetType();
              } else {
                this.lookupService.findValueset().subscribe(res => {
                  this.valuesets = res
                  if (this.valueset) {
                    this.selectedType = _.filter(this.valuesets, (obj) => obj.valueset.toLowerCase() == this.valueset.toLowerCase())[0].entity_type;
                  }
                  this.setSelectedValuesets();
                  this.updateTargetType();
                })
              }
              this.resolveEntity();
            } else {
              this.selectedType = this.types[0];
            }
          });
        }
      });
      this.geneValuesets = lookupService.GENE_VALUESETS;
    }

  ngOnInit() {
    this.formatter = (x: {label: { value: string}}) => x.label ? this.toTitleCase(x.label.value) : null;
    if (this.datasetConfig) {
      this.setSelectedValuesets();
    }
    this.updateTargetType();
  }

  onTermSelect(event) {
    if (event.item && event.item.valueset) {
      this.entity = event.item 
      this.router.navigate(['/dataset', this.datasetId, encodeURIComponent(event.item.entity), event.item.valueset]);
    }
  }

  onTypeSelect(event) {
    this.selectedType = event.target.value;      
    this.setSelectedValuesets();
  }

  findTerm(term) {
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
    return _.filter(this.valuesets, (obj) => obj.valueset.toLowerCase() == this.valueset.toLowerCase())[0].entity_type;
  }

  resolveEntity() {
    var iris = [this.iri]
    this.entity = null;
    this.lookupService.findEntityByIris(iris, data => {
      this.entity = data[0]
    });
  }

  onQueryChange(query) {
    if (query) {
      this.query = query;
    }
  }

  openDatasetAnnontation(concept) {
    var valueset = this.lookupService.findValuesetName(concept)
    this.modalService.dismissAll();
    this.router.navigate(['/dataset', this.datasetId, concept, valueset]);
  }

  openHelp(content) {
    this.modalService.open(content, { size: 'lg' });
  }

  updateTargetType(){
    this.targetType = this.BASE_PREFIX;
    if (this.selectedType == this.types[0]) {
      this.targetType = this.associationService.TYPES[this.types[1]]
    } else {
      this.targetType = this.associationService.TYPES[this.types[0]]
    }
  }

  setSelectedValuesets() {
    if (this.selectedType != 'Phenotype') {
      this.selectedValuesets = this.datasetConfig.biomedical_entity_reference_source;
    } else {
      this.selectedValuesets = this.datasetConfig.phenotype_reference_source;
    }
  }

  normalizeRef = this.associationService.normalizeRef;

}
