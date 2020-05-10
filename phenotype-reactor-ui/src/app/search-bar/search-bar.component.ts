import { Component, OnInit, SimpleChange, Output, EventEmitter, Input} from '@angular/core';
import { Observable, of } from 'rxjs';
import {debounceTime, distinctUntilChanged, tap, switchMap, catchError} from 'rxjs/operators';
import { Router } from '@angular/router';
import { TitleCasePipe } from '@angular/common';
import { LookupService } from '../lookup.service';

@Component({
  selector: 'app-search-bar',
  templateUrl: './search-bar.component.html',
  styleUrls: ['./search-bar.component.css']
})
export class SearchBarComponent implements OnInit {

  @Output() selectedTerm = new EventEmitter<any>();
  @Input() valueset =  new EventEmitter<any>();

  selectedValueset = ''
  term = null;
  searching = false;
  searchFailed = false;
  valuesets : any = [];

  formatter: any;
  
  search = (text$: Observable<string>) =>
    text$.pipe(
      debounceTime(500),
      distinctUntilChanged(),
      tap(() => this.searching = true),
      switchMap(term =>
        this.findTerm(term).pipe(
          tap(() => this.searchFailed = false),
          catchError(() => {
            this.searchFailed = true;
            return of([]);
          }))
      ),
      tap(() => this.searching = false)
    )

  constructor(private lookupService: LookupService,
    private router: Router,
    private titlecasePipe:TitleCasePipe) { }

  ngOnInit() {
    this.formatter = (x: {label: { value: string}}) => x.label ? this.toTitleCase(x.label.value) : null;

    this.lookupService.findValueset().subscribe(res => {
      this.valuesets = res
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
      return this.lookupService.findEntityByLabelStartsWith(term, this.selectedValueset)
  }

  sort(lookupList){
    return lookupList.sort((one, two) => (one.name < two.name ? -1 : 1));
  }
}
