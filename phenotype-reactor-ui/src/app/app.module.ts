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
import { ListAssociationComponent, ListAssoicationSortableHeader} from './list-association/list-association.component';
import { DownloadsComponent } from './downloads/downloads.component';
import { SparqlFormComponent } from './sparql-form/sparql-form.component';
import { ArchiveService } from './archive.service';
import { PlotScatterChartComponent } from './plot-scatter-chart/plot-scatter-chart.component';
import { NgxJsonLdModule } from '@ngx-lite/json-ld';
import { BindSchemaComponent } from './bind-schema/bind-schema.component';

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    AboutComponent,
    ISparqlComponent,
    SearchBarComponent,
    ListAssociationComponent,
    ListAssoicationSortableHeader,
    DownloadsComponent,
    SparqlFormComponent,
    PlotScatterChartComponent,
    BindSchemaComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpClientModule,
    NgbModule,
    MDBBootstrapModule.forRoot(),
    NgxJsonLdModule,
    AppRoutingModule
  ],
  providers: [LookupService, AssociationService, ArchiveService, TitleCasePipe],
  bootstrap: [AppComponent]
})
export class AppModule { }
