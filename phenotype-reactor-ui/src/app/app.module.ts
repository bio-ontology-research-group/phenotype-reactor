import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { MDBBootstrapModule } from 'angular-bootstrap-md';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomeComponent } from './home/home.component';
import { AboutComponent } from './about/about.component';
import { ISparqlComponent } from './isparql/isparql.component';
import { SearchBarComponent } from './search-bar/search-bar.component';
import { TitleCasePipe } from '@angular/common';
import { LookupService } from './lookup.service';
import { AssociationService }  from './association.service';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { ListAssociationComponent } from './list-association/list-association.component';
import { DownloadsComponent } from './downloads/downloads.component';
import { SparqlFormComponent } from './sparql-form/sparql-form.component';

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    AboutComponent,
    ISparqlComponent,
    SearchBarComponent,
    ListAssociationComponent,
    DownloadsComponent,
    SparqlFormComponent
  ],
  imports: [
    BrowserModule,
    NgbModule,
    FormsModule,
    HttpClientModule,
    MDBBootstrapModule.forRoot(),
    AppRoutingModule
  ],
  providers: [LookupService, AssociationService, TitleCasePipe],
  bootstrap: [AppComponent]
})
export class AppModule { }
