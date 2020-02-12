import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { IsparqlComponent } from './isparql.component';

describe('IsparqlComponent', () => {
  let component: IsparqlComponent;
  let fixture: ComponentFixture<IsparqlComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ IsparqlComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(IsparqlComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
