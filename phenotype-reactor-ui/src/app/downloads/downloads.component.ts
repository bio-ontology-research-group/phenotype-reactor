import { Component, OnInit } from '@angular/core';
import { ArchiveService } from '../archive.service';

@Component({
  selector: 'app-downloads',
  templateUrl: './downloads.component.html',
  styleUrls: ['./downloads.component.css']
})
export class DownloadsComponent implements OnInit {

  constructor(private archiveService: ArchiveService) { }

  files : any = [];

  ngOnInit() {
    this.archiveService.find().subscribe(res => {
      this.files = res;
    });
  }

  downloadFile(filename: string) {
    window.open(`/static/${filename}`);
  }

  downloadArchivedFile(filename: string) {
    window.open(`/archive/${filename}`);
  }

  openInNewTab(url: string) {
    window.open(url, "_blank");
  }
}
