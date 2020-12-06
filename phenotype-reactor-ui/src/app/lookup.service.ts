import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { of } from 'rxjs';
import { _ } from 'underscore';

@Injectable()
export class LookupService {

  options = {
    headers:  new HttpHeaders({
      'Accept': 'application/json'
    })
  };

  OBO_PREFIX = 'http://purl.obolibrary.org/obo/';
  ORPHA_PREFIX = 'http://www.orpha.net/ORDO/Orphanet_';
  OMIM_PREFIX = 'https://omim.org/entry/';
  DECIPHER_PREFIX = 'https://decipher.sanger.ac.uk/syndrome/';
  MGI_PREFIX = 'http://www.informatics.jax.org/marker/';
  ENTREZ_GENE_PREFIX = 'https://www.ncbi.nlm.nih.gov/gene/';
  PUBCHEM_PREFIX = 'https://pubchem.ncbi.nlm.nih.gov/compound/';

  PREFIX_TO_VALUESET_DICT = {}

  GENE_VALUESETS = ['MGI', 'NCBIGene']

  constructor(private http: HttpClient) { 
    this.PREFIX_TO_VALUESET_DICT[this.OBO_PREFIX + 'HP_'] = 'HP';
    this.PREFIX_TO_VALUESET_DICT[this.OBO_PREFIX + 'MP_'] = 'MP';
    this.PREFIX_TO_VALUESET_DICT[this.OBO_PREFIX + 'NCBITaxon_'] = 'NCBITAXON';
    this.PREFIX_TO_VALUESET_DICT[this.OBO_PREFIX + 'MONDO_'] = 'MONDO';
    this.PREFIX_TO_VALUESET_DICT[this.OBO_PREFIX + 'CHEBI_'] = 'CHEBI';
    this.PREFIX_TO_VALUESET_DICT[this.OBO_PREFIX + 'DOID_'] = 'DOID';
    this.PREFIX_TO_VALUESET_DICT[this.ORPHA_PREFIX] = 'ordo';
    this.PREFIX_TO_VALUESET_DICT[this.OMIM_PREFIX] = 'OMIM';
    this.PREFIX_TO_VALUESET_DICT[this.DECIPHER_PREFIX] = 'DECIPHER';
    this.PREFIX_TO_VALUESET_DICT[this.MGI_PREFIX] = 'MGI';
    this.PREFIX_TO_VALUESET_DICT[this.ENTREZ_GENE_PREFIX] = 'NCBIGene';
    this.PREFIX_TO_VALUESET_DICT[this.PUBCHEM_PREFIX] = 'PUBCHEM';
  }

  findValueset() {
    return this.http.get(`/api/valueset`, this.options);
  }

  findEntityByLabelStartsWith(term: string, valueset: string[]) {
    if (term === '') {
      return of([]);
    }

    var queryStr = `term=${term}`;
    valueset.forEach(function (value) {
      queryStr = queryStr + "&valueset=" + value;
    });
    return this.http.get(`/api/entity/_startswith?${queryStr}`, this.options);
  }

  findEntityByIris(iris: any[], callback) {
    var valuesetToIri = {};
    for (var i = 0; i < iris.length; i++) {
      var val = this.findValuesetName(iris[i])
      if (valuesetToIri[val]) {
        valuesetToIri[val].push(iris[i])
      } else {
        valuesetToIri[val] = [iris[i]]
      }
    }

    Object.keys(valuesetToIri).forEach(key => {
      var data = null
      if (key == 'entity') {
        data = {'iri': valuesetToIri[key]}
      } else {
        data = {'iri': valuesetToIri[key], valueset: key}
      }
      this.http.post(`/api/entity/_findbyiri`, data, this.options).subscribe( data => {
        callback(data)
      });
    });
  }

  findValuesetName(uri) {
    var props = Object.keys(this.PREFIX_TO_VALUESET_DICT)
    for (var i = 0; i < props.length; i++) {
      if (uri.includes(props[i])) {
        return this.PREFIX_TO_VALUESET_DICT[props[i]] 
      }
    }    
    return 'entity';
  }
}
