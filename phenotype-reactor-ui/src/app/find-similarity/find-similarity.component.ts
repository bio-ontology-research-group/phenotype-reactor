import { TitleCasePipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Observable, of, Subject, merge } from 'rxjs';
import {debounceTime, distinctUntilChanged, tap, switchMap, catchError} from 'rxjs/operators';
import { LookupService } from '../lookup.service';
import { _ } from 'underscore';
import { AssociationService } from '../association.service';
import { AbstractControl, FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-find-similarity',
  templateUrl: './find-similarity.component.html',
  styleUrls: ['./find-similarity.component.css']
})
export class FindSimilarityComponent implements OnInit {
  similarityForm: FormGroup;
  focus$ = new Subject<string>();
  searchFailed = false;
  selectedSourceType = '';
  selectedTargetType = '';
  sourceIri = '';
  targetIri = '';
  sourceValuesets : any = [];
  targetValuesets : any = [];
  valuesets : any = [];
  geneValuesets = [];
  types = {};
  sourceEntity = {};
  targetEntity = {};
  matchingPhenotypes = [];
  matchingPhenotypeSuperclasses = [];
  phenotypeLoading = false;
  phenotypeSuperclassesLoading = false;

  formatter = (x) => { 
    if (this.geneValuesets.includes(x.valueset)) {
      return x.label ? x.label[0] + ' ' + x.label[1] : '';
    } else {
      return x.label ? x.label[0] : '';
    }
    return '';
  }

  sourceSearch = (text$: Observable<string>) => {
    const debouncedText$ = text$.pipe(debounceTime(500), distinctUntilChanged());
    const inputFocus$ = this.focus$;
    return merge(debouncedText$, inputFocus$).pipe(
      switchMap(term =>
        this.findSourceTerm(term).pipe(
          tap(() => this.searchFailed = false),
          catchError(() => {
            this.searchFailed = true;
            return of([]);
          }))
    ));
  }

  targetSearch = (text$: Observable<string>) => {
    const debouncedText$ = text$.pipe(debounceTime(500), distinctUntilChanged());
    const inputFocus$ = this.focus$;
    return merge(debouncedText$, inputFocus$).pipe(
      switchMap(term =>
        this.findTargetTerm(term).pipe(
          tap(() => this.searchFailed = false),
          catchError(() => {
            this.searchFailed = true;
            return of([]);
          }))
    ));
  }

  constructor(private lookupService: LookupService,
    private formBuilder: FormBuilder,
    private router: Router,
    private route: ActivatedRoute, 
    private titlecasePipe:TitleCasePipe,
    private associationService: AssociationService) {
      this.lookupService.findValueset().subscribe(res => {
        this.valuesets = res
      });
      this.geneValuesets = lookupService.GENE_VALUESETS;
      this.types = Object.assign({}, associationService.TYPES);
      delete this.types['Phenotype'];

      this.route.params.subscribe( params => {
        this.sourceIri = decodeURIComponent(params.source);
        this.targetIri = decodeURIComponent(params.target);
        this.selectedSourceType = params.sourceType ? params.sourceType : ''
        this.selectedTargetType = params.targetType ? params.targetType : ''
        if (this.sourceIri && this.targetIri && this.selectedSourceType && this.selectedTargetType) {

          this.phenotypeLoading = false;
          this.associationService.findMatchingPhenotypes(this.sourceIri, this.targetIri).subscribe( data => {
            this.matchingPhenotypes = data ? data['results']['bindings'] : [];
            this.phenotypeLoading = true;
          });
          this.phenotypeSuperclassesLoading = false;
          this.associationService.findMatchingPhenotypeSuperClasses(this.sourceIri, this.targetIri).subscribe( data => {
            this.matchingPhenotypeSuperclasses = data ? this.sortAberowlClasses(data) : [];
            this.phenotypeSuperclassesLoading = true;
          });
          this.resolveEntities();
        }
      });
  }

  ngOnInit() {
    this.similarityForm = this.formBuilder.group({
      sourceType: ['', Validators.required],
      targetType: ['', Validators.required],
      sourceEntity: ['', Validators.required],
      targetEntity: ['', [Validators.required]]
    },{
      validator: this.mustNotMatchEntityValidator,
    });

    if (this.sourceIri && this.targetIri && this.selectedSourceType && this.selectedTargetType) {
      this.f.sourceType.setValue(this.selectedSourceType)
      this.f.targetType.setValue(this.selectedTargetType)
    }
  }

  // convenience getter for easy access to form fields
  get f() { return this.similarityForm.controls; }

  onSubmit() {  
    this.router.navigate(['/similarity', encodeURIComponent(this.f.sourceEntity.value.entity), this.selectedSourceType, encodeURIComponent(this.f.targetEntity.value.entity), this.selectedTargetType]);
  }

  onSourceSelect(event) {
    if (event.item && event.item.valueset) {
      this.sourceEntity = event.item;
    }
  }
  
  onTargetSelect(event) {
    if (event.item && event.item.valueset) {
      this.sourceEntity = event.item;
    }
  }

  onSourceTypeSelect(event) {
    this.selectedSourceType = event.target.value;
    this.sourceValuesets = _.map(_.filter(this.valuesets, (obj) => obj.entity_type == this.selectedSourceType), obj => obj.valueset);
    this.similarityForm.get('sourceEntity').reset();
  }

  onTargetTypeSelect(event) {
    this.selectedTargetType = event.target.value;
    this.targetValuesets = _.map(_.filter(this.valuesets, (obj) => obj.entity_type == this.selectedTargetType), obj => obj.valueset);
    this.similarityForm.get('targetEntity').reset();
  }

  findSourceTerm(term) {
      return this.lookupService.findEntityByLabelStartsWith(term, this.sourceValuesets)
  }

  findTargetTerm(term) {
      return this.lookupService.findEntityByLabelStartsWith(term, this.targetValuesets)
  }

  toTitleCase(text){
    return this.titlecasePipe.transform(text);
  }

  keys(obj) {
    return Object.keys(obj);
  }

  mustNotMatchEntityValidator(form: FormGroup): { mustNotMatch: boolean } {
    var sourceEntity = form.get('sourceEntity').value;
    var targetEntity = form.get('targetEntity').value;
    
    if (sourceEntity && targetEntity && sourceEntity.entity == targetEntity.entity) {
      return {mustNotMatch: true};
    }
    return null;
  }

  sortAberowlClasses(classes) {
    return classes.sort((one, two) => (one.label < two.label ? -1 : 1));
  }

  conceptRef(concept) {
    var valueset = this.lookupService.findValuesetName(concept)
    return `/association/${encodeURIComponent(concept)}/${valueset}`;
  }


  resolveEntities() {
    var iris = [this.sourceIri];
    this.sourceEntity = null;
    this.lookupService.findEntityByIris(iris, data => {
      this.sourceEntity = data[0];
      this.f.sourceEntity.setValue(this.sourceEntity)
    });

    var iris = [this.targetIri];
    this.targetEntity = null;
    this.lookupService.findEntityByIris(iris, data => {
      this.targetEntity = data[0];
      this.f.targetEntity.setValue(this.targetEntity)
    });
  }

  encode = encodeURIComponent;

}
