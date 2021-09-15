import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { AboutComponent } from './about/about.component';
import { ISparqlComponent } from './isparql/isparql.component';
import { DownloadsComponent } from './downloads/downloads.component';
import { GeneDiseaseComponent } from './gene-disease/gene-disease.component';
import { ListAssociationsetComponent } from './list-associationset/list-associationset.component';
import { PathogenHostTargetComponent } from './pathogen-host-target/pathogen-host-target.component';
import { DrugTargetComponent } from './drug-target/drug-target.component';
import { ViewAssociationsetComponent } from './view-associationset/view-associationset.component';
import { FindSimilarityComponent } from './find-similarity/find-similarity.component';
import { HelpComponent } from './help/help.component';
import { ApiComponent } from './api/api.component';


const routes: Routes = [
  {path: '',component: HomeComponent}, 
  {path: 'association/:iri/:valueset',component: HomeComponent}, 
  {path: 'about',component: AboutComponent},  
  {path: 'downloads',component: DownloadsComponent},  
  {path: 'isparql',component: ISparqlComponent},
  {path: 'genedisease',component: GeneDiseaseComponent},
  {path: 'genedisease/:iri/:valueset',component: GeneDiseaseComponent},
  {path: 'drugtarget',component: DrugTargetComponent},
  {path: 'drugtarget/:iri/:valueset',component: DrugTargetComponent},
  {path: 'pathogenhosttarget',component: PathogenHostTargetComponent},
  {path: 'pathogenhosttarget/:iri',component: PathogenHostTargetComponent},
  {path: 'dataset',component: ListAssociationsetComponent},
  {path: 'dataset/:identifier',component: ViewAssociationsetComponent},
  {path: 'dataset/:identifier/:iri/:valueset',component: ViewAssociationsetComponent},
  {path: 'similarity',component: FindSimilarityComponent},
  {path: 'similarity/:source/:sourceType/:target/:targetType',component: FindSimilarityComponent},
  {path: 'help',component: HelpComponent},
  {path: 'docs',component: ApiComponent},
];


@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
