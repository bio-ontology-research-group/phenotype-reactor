import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ListSimilarAssociationsComponent } from './list-similar-associations.component';

describe('ListSimilarAssociationsComponent', () => {
  let component: ListSimilarAssociationsComponent;
  let fixture: ComponentFixture<ListSimilarAssociationsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ListSimilarAssociationsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ListSimilarAssociationsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
