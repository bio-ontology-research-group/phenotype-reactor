import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ListAssociationComponent } from './list-association.component';

describe('ListAssociationComponent', () => {
  let component: ListAssociationComponent;
  let fixture: ComponentFixture<ListAssociationComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ListAssociationComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ListAssociationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
