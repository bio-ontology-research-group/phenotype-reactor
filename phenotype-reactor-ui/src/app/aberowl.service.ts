import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { of } from 'rxjs';
import { map } from 'rxjs/operators';

export enum ONT {
  NCBITAXON = "NCBITAXON",
  DOID = "DOID",
  HP = "HP",
  MP = "MP"
}

@Injectable()
export class AberowlService {

  ABEROWL_API_URL = 'http://aber-owl.net/api'

  options = {
    headers:  new HttpHeaders({
      'Accept': 'application/json'
    })
  };

  constructor(private http: HttpClient) { }

  findDiseases(term) {
    return this.findClassByNameStartsWith(term, [ONT.DOID])
  }

  findPhenotypes(term) {
    return this.findClassByNameStartsWith(term, [ONT.HP, ONT.MP])
  }

  findPathogens(term) {
    return this.findClassByNameStartsWith(term, [ONT.NCBITAXON])
  }

  findClassByNameStartsWith(term: string, ontologies: string[]) {
    if (term === '') {
      return of([]);
    }

    var ontologyPartStr = ''
    for (var index in ontologies) {
      ontologyPartStr += '&ontology=' + ontologies[index]
    }
    return this.http.get(`${this.ABEROWL_API_URL}/class/_startwith?query=${term}${ontologyPartStr}`, this.options)
      .pipe(map(response => response ? response['result'] : []));
  }
  
}
