import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { AboutComponent } from './about/about.component';
import { ISparqlComponent } from './isparql/isparql.component';
import { DownloadsComponent } from './downloads/downloads.component';
import { GeneDiseaseComponent } from './gene-disease/gene-disease.component';
import { ListAssociationsetComponent } from './list-associationset/list-associationset.component';
import { PathogenHostTargetComponent } from './pathogen-host-target/pathogen-host-target.component';


const routes: Routes = [
  {path: '',component: HomeComponent}, 
  {path: 'association/:iri/:valueset',component: HomeComponent}, 
  {path: 'about',component: AboutComponent},  
  {path: 'downloads',component: DownloadsComponent},  
  {path: 'isparql',component: ISparqlComponent},
  {path: 'genedisease',component: GeneDiseaseComponent},
  {path: 'genedisease/:iri/:valueset',component: GeneDiseaseComponent},
  {path: 'pathogenhosttarget',component: PathogenHostTargetComponent},
  {path: 'pathogenhosttarget/:iri',component: PathogenHostTargetComponent},
  {path: 'dataset',component: ListAssociationsetComponent},
];


@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
