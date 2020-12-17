import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Injectable()
export class AssociationService {

  URL = '/api/association'

  TYPES = {
    'Drug' : { name: 'Drug',  uri: 'http://phenomebrowser.net/Drug' },
    'Disease' : { name: 'Disease',  uri: 'http://phenomebrowser.net/Disease' },
    'Gene' : { name: 'Gene', uri: 'http://phenomebrowser.net/Gene' },
    'Metabolite' : { name: 'Metabolite', uri: 'http://phenomebrowser.net/Metabolite' },
    'Pathogen' : { name: 'Pathogen', uri: 'http://phenomebrowser.net/Pathogen' },
    'Phenotype' : { name: 'Phenotype', uri: 'http://phenomebrowser.net/Phenotype' }
  }

  EVIDENCE = {
    'ECO_0006016' : { name: 'author statement from published clinical study', uri: 'http://purl.obolibrary.org/obo/ECO_0006016' },
    'ECO_0000033' : { name: 'author statement supported by traceable reference',  uri: 'http://purl.obolibrary.org/obo/ECO_0000033' },
    'ECO_0007669' : { name: 'computational evidence used in automatic assertion', uri: 'http://purl.obolibrary.org/obo/ECO_0007669' },
    'ECO_0000305' : { name: 'curator inference used in manual assertion',  uri: 'http://purl.obolibrary.org/obo/ECO_0000305' },
    'ECO_0000501' : { name: 'inferred from electronic annotation', uri: 'http://purl.obolibrary.org/obo/ECO_0000501' },
    'ECO_0006018' : { name: 'inference based on individual clinical experience',  uri: 'http://purl.obolibrary.org/obo/ECO_0006018' },
    'ECO_0000251' : { name: 'similarity evidence used in automatic assertion', uri: 'http://purl.obolibrary.org/obo/ECO_0000251' }
  }

  options = {
    headers:  new HttpHeaders({
      'Accept': 'application/json'
    })
  };

  constructor(private http: HttpClient) { }

  find(conceptIri: string, phenotypeIri: string, typeIri:string, evidenceIris:string[], associationsetIris:string[], limit:number, offset:number, orderBy:string) {
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

    for (var i=0; i < evidenceIris.length; i++) {
      query_string += query_string ? '&' : '';
      query_string += 'evidence=' + evidenceIris[i];
    }

    for (var i=0; i < associationsetIris.length; i++) {
      query_string += query_string ? '&' : '';
      query_string += 'associationset=' + associationsetIris[i];
    }

    if (limit) {
      query_string += '&limit=' + limit;
    }
    
    if (offset) {
      query_string += '&offset=' + offset;
    }

    if (orderBy) {
      query_string += '&orderBy=' + orderBy;
    }

    var url = `${this.URL}?${query_string}`;
    return this.http.get(url, this.options);
  }

  findMostSimilar(iri: string, typeIri: string, orderBy:string, limit:number) {
    var query_string = 'concept=' + iri;
    if (typeIri) {
      query_string = query_string + '&type=' + typeIri
    }

    if (orderBy) {
      query_string += '&orderBy=' + orderBy;
    }

    if (limit) {
      query_string += '&limit=' + limit;
    }
    var url = `${this.URL}/_mostsimilar?${query_string}`;
    return this.http.get(url, this.options);
  }

  findMatchingPhenotypes(sourceIri: string, targetIri: string) {
    var url = `api/association/matching-phenotypes?source=${sourceIri}&target=${targetIri}`;
    return this.http.get(url, this.options);
  }

  findMatchingPhenotypeSuperClasses(sourceIri: string, targetIri: string) {
    var url = `api/association/matching-phenotype-superclasses?source=${sourceIri}&target=${targetIri}`;
    return this.http.get(url, this.options);
  }
  
  findAssociationset() {
    return this.http.get(`/api/associationset`, this.options);
  }
  
}
