import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SparqlFormComponent } from './sparql-form.component';

describe('SparqlFormComponent', () => {
  let component: SparqlFormComponent;
  let fixture: ComponentFixture<SparqlFormComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SparqlFormComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SparqlFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
