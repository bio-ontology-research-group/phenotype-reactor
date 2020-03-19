import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { of } from 'rxjs';
import { map } from 'rxjs/operators';

export enum ENTITY_TYPE {
  PATHOGEN = "PATHOGEN",
  DRUG = "DRUG",
  DISEASE = "Disease",
  PHENOTYPE = "Phenotype",
  GENE = "Gene"
}

@Injectable()
export class LookupService {

  options = {
    headers:  new HttpHeaders({
      'Accept': 'application/json'
    })
  };

  constructor(private http: HttpClient) { }

  findDiseases(term) {
    return this.findEntityByLabelStartsWith(term, ENTITY_TYPE.DISEASE)
  }

  findPhenotypes(term) {
    return this.findEntityByLabelStartsWith(term, ENTITY_TYPE.PHENOTYPE)
  }

  findPathogens(term) {
    return this.findEntityByLabelStartsWith(term, ENTITY_TYPE.PATHOGEN)
  }

  findEntityByLabelStartsWith(term: string, entityType: string) {
    if (term === '') {
      return of([]);
    }

    return this.http.get(`/api/entity/_startswith?term=${term}&entitytype${entityType}`, this.options)
      .pipe(map(response => response ? response['result'] : []));
  }
  
}
