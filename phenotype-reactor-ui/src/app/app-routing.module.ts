import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { AboutComponent } from './about/about.component';
import { ISparqlComponent } from './isparql/isparql.component';
import { DownloadsComponent } from './downloads/downloads.component';


const routes: Routes = [
  {path: '',component: HomeComponent}, 
  {path: 'association/:iri/:valueset',component: HomeComponent}, 
  {path: 'about',component: AboutComponent},  
  {path: 'downloads',component: DownloadsComponent},  
  {path: 'isparql',component: ISparqlComponent}
];


@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
