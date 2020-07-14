import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Injectable()
export class AssociationService {

  URL = '/api/association'

  TYPES = [
    { name: 'Drug', uri: 'http://phenomebrowser.net/Drug' },
    { name: 'Disease', uri: 'http://phenomebrowser.net/Disease' },
    { name: 'Gene', uri: 'http://phenomebrowser.net/Gene' },
    { name: 'Metabolite', uri: 'http://phenomebrowser.net/Metabolite' },
    { name: 'Pathogen', uri: 'http://phenomebrowser.net/Pathogen' },
    { name: 'Phenotype', uri: 'http://phenomebrowser.net/Phenotype' }
  ]

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

  findMostSimilar(iri: string, typeIri: string) {
    var query_string = 'concept=' + iri;
    if (typeIri) {
      query_string = query_string + '&type=' + typeIri
    }

    var url = `${this.URL}/_mostsimilar?${query_string}`;
    return this.http.get(url, this.options);
  }
  
}
