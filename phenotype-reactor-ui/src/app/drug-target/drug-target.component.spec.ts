import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DrugTargetComponent } from './drug-target.component';

describe('DrugTargetComponent', () => {
  let component: DrugTargetComponent;
  let fixture: ComponentFixture<DrugTargetComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DrugTargetComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DrugTargetComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
