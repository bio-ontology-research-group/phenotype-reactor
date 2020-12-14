import { Component, OnInit, SimpleChange, Output, EventEmitter, Input, ViewChild, ElementRef} from '@angular/core';
import { Observable, of, Subject, merge } from 'rxjs';
import {debounceTime, distinctUntilChanged, tap, switchMap, catchError} from 'rxjs/operators';
import { Router } from '@angular/router';
import { TitleCasePipe } from '@angular/common';
import { LookupService } from '../lookup.service';
import { _ } from 'underscore';
import { NgbModal, NgbTypeahead } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-search-bar',
  templateUrl: './search-bar.component.html',
  styleUrls: ['./search-bar.component.css']
})
export class SearchBarComponent implements OnInit {

  @ViewChild('searchInput', {static: true}) searchInput:ElementRef; 
  @ViewChild('instance', {static: true}) instance: NgbTypeahead;
  @Output() selectedTerm = new EventEmitter<any>();
  @Input() valueset =  new EventEmitter<any>();
  
  focus$ = new Subject<string>();

  selectedValueset = ''
  term = null;
  searching = false;
  searchFailed = false;
  valuesets : any = [];
  geneValuesets = [];

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
    private titlecasePipe:TitleCasePipe,
    private modalService: NgbModal) { 
      this.geneValuesets = lookupService.GENE_VALUESETS;
    }

  ngOnInit() {
    this.formatter = (x: {label: { value: string}}) => x.label ? this.toTitleCase(x.label.value) : null;

    this.lookupService.findValueset().subscribe(res => {
      this.valuesets = res
      this.valuesets = _.filter(this.valuesets, (obj) => obj.valueset != 'ECO' && !obj.custom);
      this.sort(this.valuesets)
    })
  }

  ngOnChanges(change: SimpleChange) {
    if(change && change['valueset']) {
      this.selectedValueset = change['valueset'].currentValue
    }
  }

  onTermSelect(event){
    this.selectedTerm.emit(event.item);
  }

  toTitleCase(text){
    return this.titlecasePipe.transform(text);
  }

  onSearchValuesetSelect(event) {
    this.selectedValueset = event.target.value;
  }

  findTerm(term) {
      var valuesets = [];
      if (this.selectedValueset) {
        valuesets.push(this.selectedValueset)
      }
      return this.lookupService.findEntityByLabelStartsWith(term, valuesets);
  }

  sort(lookupList) {
    return lookupList.sort((one, two) => (one.name < two.name ? -1 : 1));
  }

  setExample(term, valueset) {
    if (!valueset) {
      this.selectedValueset = ''
    } else {
      this.selectedValueset = valueset;
    }

    this.searchInput.nativeElement.value = term;
    this.searchInput.nativeElement.focus();
  }

  openConcept(concept) {
    var valueset = this.lookupService.findValuesetName(concept)
    this.router.navigate(['/association', concept, valueset]);
  }

  openHelp(content) {
    this.modalService.open(content, { size: 'lg' });
  }
  
}
