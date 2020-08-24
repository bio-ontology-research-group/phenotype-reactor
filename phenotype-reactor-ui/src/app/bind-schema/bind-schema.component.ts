import { Component, OnInit, SimpleChange, Input } from '@angular/core';

@Component({
  selector: 'app-bind-schema',
  template: `
    <ngx-json-ld [json]="schema"></ngx-json-ld>
  `
})
export class BindSchemaComponent implements OnInit {
  BIO_SCHEMA_CONTEXT = 'https://bioschemas.org'
  SCHEMA_CONTEXT = 'http://schema.org'

  @Input() entity = null;
  schema = null;

  constructor() { }

  ngOnInit() {
  }

  ngOnChanges(change: SimpleChange) {
    if(change && change['entity'] && this.entity) {
      let identifier = this.entity.identifier ? this.entity.identifier : null;
      let alternateName = this.entity.synonym && this.entity.synonym.length > 0 ? this.entity.synonym[0] : null;
      let definition = this.entity.definition && this.entity.definition.length > 0 ? this.entity.definition[0] : null;
      let type = null;
      let context = this.SCHEMA_CONTEXT;
    
      if (this.entity.entity_type == 'Disease') {
        type = 'MedicalCondition'
      } else if (this.entity.entity_type == 'Drug') {
        type = 'Drug'
      } else if (this.entity.entity_type == 'Gene') {
        type = 'Gene'
        context = this.BIO_SCHEMA_CONTEXT
      } else if (this.entity.entity_type == 'Metabolite') {
        type = 'ChemicalSubstance'
        context = this.BIO_SCHEMA_CONTEXT
      } else if (this.entity.entity_type == 'Pathogen') {
        type = 'Thing'
      } else if (this.entity.entity_type == 'Phenotype') {
        type = 'Thing'
      } else {
        type = 'Thing'
      }
      this.schema = {
        '@context': context,
        '@type': type,
        name: this.entity.label[0],
        url: this.entity.entity,
        description: definition,
        identifier: identifier,
        alternateName: alternateName
      }
    }
  }
}
