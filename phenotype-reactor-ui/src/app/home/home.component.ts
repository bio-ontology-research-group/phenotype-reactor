import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {

  ontologyClass  : any = null

  constructor() { }

  ngOnInit() {
  }

  onTermSelect(lookupResource){
    console.log(lookupResource)
    if (lookupResource && lookupResource.ontology) {
      this.ontologyClass = lookupResource
    }
    // if (lookupResource.type.value === 'http://ddiem.phenomebrowser.net/Disease') {
    //   this.router.navigate(['/disease', encodeURIComponent(lookupResource.resource.value)]);
    // }  else {
    //   this.router.navigate(['/disease-list-by-resource', encodeURIComponent(lookupResource.resource.value), encodeURIComponent(lookupResource.type.value)]);
    // }
  }

  openInNewTab(url: string){
    window.open(url, "_blank");
  }

}
