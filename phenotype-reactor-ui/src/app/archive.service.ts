import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { of } from 'rxjs';
import { map } from 'rxjs/operators';

@Injectable()
export class ArchiveService {

  options = {
    headers:  new HttpHeaders({
      'Accept': 'application/json'
    })
  };

  constructor(private http: HttpClient) { }

  find() {
    return this.http.get(`/archive`, this.options);
  }
}
