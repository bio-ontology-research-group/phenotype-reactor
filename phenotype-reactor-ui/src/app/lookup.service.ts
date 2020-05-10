import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { of } from 'rxjs';
import { map } from 'rxjs/operators';

@Injectable()
export class LookupService {

  options = {
    headers:  new HttpHeaders({
      'Accept': 'application/json'
    })
  };

  constructor(private http: HttpClient) { }

  findValueset() {
    return this.http.get(`/api/valueset`, this.options);
  }

  findEntityByLabelStartsWith(term: string, valueset: string) {
    if (term === '') {
      return of([]);
    }

    return this.http.get(`/api/entity/_startswith?term=${term}&valueset=${valueset}`, this.options);
  }

  findEntityByIris(iris: any[]) {
    var data = {'iri': iris}
    return this.http.post(`/api/entity/_findbyiri`, data, this.options);
  }
}
