import { TitleCasePipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { LookupService } from '../lookup.service';
import { Observable, of, Subject, merge } from 'rxjs';
import {debounceTime, distinctUntilChanged, tap, switchMap, catchError} from 'rxjs/operators';
import { _ } from 'underscore';


@Component({
  selector: 'app-pathogen-host-target',
  templateUrl: './pathogen-host-target.component.html',
  styleUrls: ['./pathogen-host-target.component.css']
})
export class PathogenHostTargetComponent implements OnInit {

  BASE_PREFIX = "http://phenomebrowser.net/"
  focus$ = new Subject<string>();
  term = null;
  searching = false;
  searchFailed = false;
  conceptRedirect = "association";

  iri = null;
  valueset = 'NCBITaxon_Pathopheno';
  entity = null;
  sourceType = this.BASE_PREFIX + 'Pathogen';

  active = 1;

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
  encode = encodeURIComponent;

  constructor(private lookupService: LookupService,
    private router: Router,
    private route: ActivatedRoute, 
    private titlecasePipe:TitleCasePipe,
    private modalService: NgbModal) { 
      this.route.params.subscribe( params => {
        if (params.iri) {
          this.iri = decodeURIComponent(params.iri);
          this.active = 1;
          this.resolveEntity();
        }
      });
    }

  ngOnInit() {
    this.formatter = (x: {label: { value: string}}) => x.label ? this.toTitleCase(x.label.value) : null;
  }

  onTermSelect(event) {
    if (event.item) {
      this.entity = event.item 
      this.router.navigate(['/pathogenhosttarget', encodeURIComponent(event.item.entity)]);
    }
  }

  findTerm(term) {
      return this.lookupService.findEntityByLabelStartsWith(term, [this.valueset])
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

  resolveEntity() {
    var iris = [this.iri]
    this.entity = null;
    this.lookupService.findEntityByIris(iris, data => {
      this.entity = data[0]
    });
  }

  pathogenHostTargetRef(concept) {
    var valueset = this.lookupService.findValuesetName(concept)
    this.modalService.dismissAll();
    return `/pathogenhosttarget/${encodeURIComponent(concept)}`;
  }


  conceptRef(concept, valueset) {
    var valueset = this.lookupService.findValuesetName(concept)
    return `/association/${encodeURIComponent(concept)}/${valueset}`;
  }

  onQueryChange(query) {
    // if (query) {
    //   this.query = query;
    // }
  }
}
