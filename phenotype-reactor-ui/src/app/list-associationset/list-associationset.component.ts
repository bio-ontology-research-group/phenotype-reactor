import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AssociationService } from '../association.service';

@Component({
  selector: 'app-list-associationset',
  templateUrl: './list-associationset.component.html',
  styleUrls: ['./list-associationset.component.css']
})
export class ListAssociationsetComponent implements OnInit {

  associationsets = [];

  constructor(private router: Router,
    private route: ActivatedRoute, 
    private associationService: AssociationService) { }

  ngOnInit() {
    this.associationService.findAssociationset().subscribe(res => {
      this.associationsets = res['results']['bindings'];
    });
  }
}
