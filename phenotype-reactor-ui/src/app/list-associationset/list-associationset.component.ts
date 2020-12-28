import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AssociationService } from '../association.service';

@Component({
  selector: 'app-list-associationset',
  templateUrl: './list-associationset.component.html',
  styleUrls: ['./list-associationset.component.css']
})
export class ListAssociationsetComponent implements OnInit {

  PUBMED_PREFIX = "https://pubmed.ncbi.nlm.nih.gov/";
  associationsets = [];

  constructor(private router: Router,
    private route: ActivatedRoute, 
    private associationService: AssociationService) { }

  ngOnInit() {
    this.associationService.findAssociationset().subscribe(res => {
      this.associationsets = res['results']['bindings'];
    });
  }

  normalizeRef(url:string) {
    if (url.startsWith(this.PUBMED_PREFIX)){
      return url.replace(this.PUBMED_PREFIX, 'PMID:')
    }
    return null;
  }
}
