import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PlotScatterChartComponent } from './plot-scatter-chart.component';

describe('PlotScatterChartComponent', () => {
  let component: PlotScatterChartComponent;
  let fixture: ComponentFixture<PlotScatterChartComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PlotScatterChartComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PlotScatterChartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
