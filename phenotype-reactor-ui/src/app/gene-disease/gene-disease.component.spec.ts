import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { GeneDiseaseComponent } from './gene-disease.component';

describe('GeneDiseaseComponent', () => {
  let component: GeneDiseaseComponent;
  let fixture: ComponentFixture<GeneDiseaseComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ GeneDiseaseComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(GeneDiseaseComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
