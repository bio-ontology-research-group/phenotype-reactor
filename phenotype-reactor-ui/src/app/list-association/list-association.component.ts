import { Component, OnInit, Input } from '@angular/core';

@Component({
  selector: 'app-list-association',
  templateUrl: './list-association.component.html',
  styleUrls: ['./list-association.component.css']
})
export class ListAssociationComponent implements OnInit {

  @Input() associations = []

  page = 1;
  pageSize = 10;
  collectionSize = 0

  constructor() { }

  ngOnInit() {
    this.collectionSize = this.associations ? this.associations.length : 0;
  }

  get associationsPage(): Object[] {
    return this.associations ? this.associations
      .map((association, i) => ({id: i + 1, ...association}))
      .slice((this.page - 1) * this.pageSize, (this.page - 1) * this.pageSize + this.pageSize) : []; 
  }
}
