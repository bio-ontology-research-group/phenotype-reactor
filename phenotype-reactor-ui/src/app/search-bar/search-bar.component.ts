import { Component, OnInit, SimpleChange, Output, EventEmitter} from '@angular/core';
import { Observable, of } from 'rxjs';
import {debounceTime, distinctUntilChanged, tap, switchMap, catchError} from 'rxjs/operators';
import { Router } from '@angular/router';
import { TitleCasePipe } from '@angular/common';
import { AberowlService } from '../aberowl.service';

@Component({
  selector: 'app-search-bar',
  templateUrl: './search-bar.component.html',
  styleUrls: ['./search-bar.component.css']
})
export class SearchBarComponent implements OnInit {

  @Output() selectedTerm = new EventEmitter<any>();

  selectedSearchMode = ''
  term = null;
  searching = false;
  searchFailed = false;

  types = [
    {name: 'Device', index: 0},
    {name: 'Disease', index: 1},
    {name: 'Drug', index: 2},
    {name: 'Gene', index: 3},
    {name: 'Pathogen', index: 4},
    {name: 'Phenotype', index: 5}
  ];

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

  constructor(private aberowlService: AberowlService,
    private router: Router,
    private titlecasePipe:TitleCasePipe) { }

  ngOnInit() {
    this.formatter = (x: {label: { value: string}}) => x.label ? this.toTitleCase(x.label.value) : null;
  }

  ngOnChanges(change: SimpleChange) {
    if(change.currentValue && change.currentValue.diseaseList) {
      // TODO
    }
  }

  onTermSelect(event){
    this.selectedTerm.emit(event.item);
  }

  toTitleCase(text){
    return this.titlecasePipe.transform(text);
  }

  onSearchModeSelect(event) {
    this.selectedSearchMode = event.target.value;
  }

  findTerm(term) {
      switch (this.selectedSearchMode) {
        case '1':
          return this.aberowlService.findDiseases(term);
          break;
        case '4':
            return this.aberowlService.findPathogens(term);
            break;
        case '5':
          return this.aberowlService.findPhenotypes(term);
          break;
        default:
          return this.aberowlService.findDiseases(term);
          break;
    }
  }
}
