import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { FindSimilarityComponent } from './find-similarity.component';

describe('FindSimilarityComponent', () => {
  let component: FindSimilarityComponent;
  let fixture: ComponentFixture<FindSimilarityComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ FindSimilarityComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(FindSimilarityComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
