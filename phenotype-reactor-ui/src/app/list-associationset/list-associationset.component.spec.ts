import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ListAssociationsetComponent } from './list-associationset.component';

describe('ListAssociationsetComponent', () => {
  let component: ListAssociationsetComponent;
  let fixture: ComponentFixture<ListAssociationsetComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ListAssociationsetComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ListAssociationsetComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
