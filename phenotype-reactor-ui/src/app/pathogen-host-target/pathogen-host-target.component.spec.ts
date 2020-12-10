import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PathogenHostTargetComponent } from './pathogen-host-target.component';

describe('PathogenHostTargetComponent', () => {
  let component: PathogenHostTargetComponent;
  let fixture: ComponentFixture<PathogenHostTargetComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PathogenHostTargetComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PathogenHostTargetComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
