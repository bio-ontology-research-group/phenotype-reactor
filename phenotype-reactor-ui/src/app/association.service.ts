import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Injectable()
export class AssociationService {

  URL = '/api/association'

  options = {
    headers:  new HttpHeaders({
      'Accept': 'application/json'
    })
  };

  constructor(private http: HttpClient) { }


  find(conceptIri: string, phenotypeIri: string, typeIri:string) {
    var query_string = '';
    if (conceptIri) {
      query_string += 'concept=' + conceptIri;
    }

    if (phenotypeIri) {
      query_string += query_string ? '&' : '';
      query_string += 'phenotype=' + phenotypeIri;
    }

    if (typeIri) {
      query_string += query_string ? '&' : '';
      query_string += 'type=' + typeIri;
    }

    var url = `${this.URL}?${query_string}`;
    return this.http.get(url, this.options);
  }
  
}
