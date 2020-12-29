import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ViewAssociationsetComponent } from './view-associationset.component';

describe('ViewAssociationsetComponent', () => {
  let component: ViewAssociationsetComponent;
  let fixture: ComponentFixture<ViewAssociationsetComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ViewAssociationsetComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ViewAssociationsetComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
