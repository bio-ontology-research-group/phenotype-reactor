import { Component } from '@angular/core';
import{ Router, NavigationEnd } from '@angular/router';

declare let gtag: Function;
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'phenotype-reactor-ui';

  openInNewTab(url: string) {
    window.open(url, "_blank");
  }

  constructor(public router: Router){ 
    this.router.events.subscribe(event => {
      if(event instanceof NavigationEnd) {
        gtag('config', 'G-246QDR6JDG', { 'page_path': event.urlAfterRedirects });
      }
    });
  }
}
