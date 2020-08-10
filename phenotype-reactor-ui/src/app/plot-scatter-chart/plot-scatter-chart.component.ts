import { Component, OnInit, Input, ViewChild, ElementRef, SimpleChange } from '@angular/core';
import * as d3 from 'd3';
import d3Tip from "d3-tip" 

@Component({
  selector: 'app-plot-scatter-chart',
  templateUrl: './plot-scatter-chart.component.html',
  styleUrls: ['./plot-scatter-chart.component.css']
})
export class PlotScatterChartComponent implements OnInit {

  @Input() similarConcepts = []
  @Input() similarEntities = []
  @ViewChild("chart" , {static: true}) chartEle: ElementRef;

  x = null;
  y = null;
  margin = {
    top: 50,
    right: 200,
    bottom: 50,
    left: 50
  }
  r = 5;
  legendWidth = 1200;
  outerWidth = 900;
  outerHeight = 450;

  constructor() { }

  ngOnInit() {
  }

  ngOnChanges(change: SimpleChange) {
    if(change && change['similarConcepts']) {
      this.plot(this.similarConcepts)
    }
  }

  plot(data) {
    var that = this
    var width = this.outerWidth - this.margin.left - this.margin.right;
    var height = this.outerHeight - this.margin.top - this.margin.bottom;
      
    var padding = 0;
    var currentTransform = null;

    var types = new Set<string>();
    data.forEach(function(d) {
      types.add(that.localName(d.type.value));
    });
    var typeArray = [...types];
    this.x = d3.scaleLinear()
      .domain(d3.extent(data, d => {
        return parseFloat(d['x']['value'])
      }))
      .range([padding, width - padding])
      .nice();

    this.y = d3.scaleLinear()
      .domain(d3.extent(data, d => {
        return parseFloat(d['y']['value'])
      }))
      .range([height, 0])
      .nice();

    var zoom = d3.zoom().on("zoom", () => {
      x_axis.call(xAxis.scale(d3.event.transform.rescaleX(this.x)));
      y_axis.call(yAxis.scale(d3.event.transform.rescaleY(this.y)));
  
  
      // re-draw circles using new x-axis & y-axis 
      var new_y = d3.event.transform.rescaleY(this.y);
      dots.attr("cy", function(d) {
        return new_y(parseFloat(d['y']['value']));
      });
      var new_x = d3.event.transform.rescaleX(this.x);
      dots.attr("cx", function(d) {
        return new_x(parseFloat(d['x']['value']));
      });
    });

    var color = d3.scaleOrdinal(d3.schemeCategory10).domain(typeArray);

    var tip = d3Tip();
    tip
      .attr('class', 'd3-tip')
      .offset([-10, 0])
      .html(function(d) {
        var entity = that.similarEntities[d.concept.value]
        if (entity) {
          return "name: " + entity['label'][0] + "<br>" + "id : " + d.concept.value;
        } else {
          return "name: " + d.concept.value //"<br>" + "id : " + d.id;
        }
      })
    
    d3.select("svg").remove(); 
    var chart = d3.select(this.chartEle.nativeElement)
          .append('svg:svg')
          .attr('width', this.legendWidth)
          .attr('height', this.outerHeight)
          .attr("fill", "white")
          .attr('class', 'chart')
          .append("g")
          .attr("transform", "translate(" + this. margin.left + "," + this.margin.top + " )")
          .call(zoom);
    chart.call(tip);

    chart.append("rect")
          .attr("width", width)
          .attr("height", height);

    var xAxis = d3.axisBottom(this.x).tickSize(-height);
    var x_axis = chart.append('g')
      .attr('transform', 'translate(0,' + height + ')')
      .attr('class', 'x axis')
      .call(xAxis);

    var yAxis = d3.axisLeft(this.y).tickSize(-width);
    var y_axis = chart.append('g')
      .attr('transform', 'translate(0,0)')
      .attr('class', 'y axis')
      .call(yAxis)


    var objects = chart.append("svg")
      .classed("objects", true)
      .attr("width", width)
      .attr("height", height);

    var dots = objects.selectAll(".dot")
      .data(data)
      .enter().append("circle")
      .attr("cx", d => {
        return this.x(parseFloat(d['x']['value']));
      })
      .attr("cy",  d => { 
        return this.y(parseFloat(d['y']['value']));
      })
      .attr("fill", d => {
        return color(that.localName(d['type']['value']));
      })
      .attr("r", 5)
      .on("mouseover",function(d) { tip.show(d, this) }) 
      .on("mouseout",function(d) { tip.hide(d,this ) });
      
      //add legand
      var legendSpace = 20;
      var i = 0;
      
      types.forEach(type => {
        chart.append("circle")
        .attr("r", this.r)
        .attr("cx", width + (this.margin.bottom / 2) + 5)
        .attr("cy", (legendSpace / 2) + i * legendSpace)
        .attr("fill", function() { 
          return color('' + type);
        });

        chart.append("text")
          .attr("x", width + (this.margin.bottom / 2) + 13) // space legend
          .attr("y", ((legendSpace / 2) + i * legendSpace) + 5)
          .attr("class", "legend") // style the legend
          .style("fill", function() { 
            return "#3d3d3d";
        }).text('' + type);
        i++;
      });
  }

  transform(d) {
    return "translate(" + d3.event.transform.rescaleX(parseFloat(d['x']['value'])) + "," + d3.event.transform.rescaleY(parseFloat(d['y']['value'])) + ")";
  }

  localName(type) {
    return type.split('/')[type.split('/').length - 1];
  }
}
