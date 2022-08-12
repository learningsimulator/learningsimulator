$(document).ready(function() {

  $('.resizable_e').resizable({
    handles: 'e'
  });

  $('.resizable_s').resizable({
    handles: 's'
  });

  // Hummingbird (list/tree of checkboxes) initialization
  $.fn.hummingbird.defaults.collapsedSymbol = "fa-arrow-circle-right";
  $.fn.hummingbird.defaults.expandedSymbol = "fa-arrow-circle-down";
  $.fn.hummingbird.defaults.checkDoubles = false;

  $("#treeview").hummingbird();

  // amCharts configuration
  // am4core.useTheme(am4themes_animated);
  am4core.options.autoDispose = true;

  // Set event listener to checkboxes in "My datasets" list
  $('.my_datasets_list').change(function(event) {
    render_plots();
  });

  // Set event listener to checkboxes in "Predefined datasets" tree

  // This does not work for some reason...
  // $("#treeview").on("nodeChecked", function(){
  //   alert("jjj");
  //   render_plots();
  // });
  // $("#treeview").on("nodeUnchecked", render_plots);

  // ...so we do this instead
  $('.hummingbird-treeview').change(function(event) {
    render_plots();
  });

  // Set event listener to controls in Control panel
  $('#stack_plots_checkbox').change(function(event) {
    render_plots();
  });
  $('#log_time_checkbox').change(function(event) {
    render_plots();
  });
  $('#time_unit').change(function(event) {
    render_plots();
  });
  $('#input_current_year').change(function(event) {
    render_plots();
  });
  

//  async function render_plots() {
  function render_plots() {
    // if (event.target.checked) {   // Or event.target.value
    //   // The checkbox is now checked 
    // } else {
    //   // The checkbox is now no longer checked
    // }

    let checked_ids = [];
    let checked_checkboxes = $('input:checkbox.my_datasets_checkbox:checked');
    for (let i = 0; i < checked_checkboxes.length; i++) {
      checked_ids.push(checked_checkboxes[i].id);
    }

    var predef_checked_ids = {"id": checked_ids, "dataid": [], "text": []};
    $("#treeview").hummingbird("getChecked", {list:predef_checked_ids, onlyEndNodes:true, onlyParents:false, fromThis:false});
    checked_ids = predef_checked_ids.id.join(",");

    am4core.disposeAllCharts();
    if (checked_ids.length > 0) {
      fetch("/get_for_plot/" + checked_ids).then(response => response.json()).then(plotdata => plot(plotdata));
      // const plotdata = await fetch("/get_for_plot_predef/" + checked_ids).then(response => response.json());
      
    }
  }


  // function isNumeric(str) {
  //   return !isNaN(str) && // use type coercion to parse the _entirety_ of the string (`parseFloat` alone does not do this)...
  //          !isNaN(parseFloat(str)) // ...and ensure strings of whitespace fail
  // }

  var timeAxes = [];
  var valueAxes = [];
  
  function plot(plotdata) {
    const nTimelines = plotdata.legends.length;
    // alert(plotdata.data_is_qualitative);
    // alert(plotdata.xydata[0]);
    // if (plotdata.xydata.length !== plotdata.legends.length) {
    //   throw new Error("Assertion failed");
    // }

    var is_stacked = document.getElementById('stack_plots_checkbox').checked;

    const chartstack = document.getElementById("chartstack");

    // Remove all divs inside <p id="chartstack">
    while (chartstack.firstChild) {
      chartstack.removeChild(chartstack.lastChild);
    }    
    
    let nCharts = 1;
    if (is_stacked) {
      nCharts = nTimelines;
    }

    let chartdata = plotdata.xydata;

    // Convert time string to Date-objects (e.g. from "1854" to new Date("1854"))
    for (let i = 0; i < chartdata.length; i++) {
      let dict = chartdata[i];
      for (let key in dict) {
        if (key.startsWith("time")) {
          chartdata[i][key] = new Date(chartdata[i][key]);
        }
      }
    }

    // Transform time axis values to Years Before Current (YBC) if set
    let timeUnit = document.getElementById("time_unit").value;
    let isLogTime = document.getElementById("log_time_checkbox").checked;
    let isYBC = (timeUnit === "ybc");
    if (isYBC) {
      let MS_PER_YEAR =  1000 * 60 * 60 * 24 * 365.25;
      currentDateStr = document.getElementById("input_current_year").value;
      currentDate = new Date(currentDateStr);
      for (let i = 0; i < chartdata.length; i++) {
        let dict = chartdata[i];
        for (let key in dict) {
          if (key.startsWith("time")) {
            let diffMs = currentDate.getTime() - chartdata[i][key].getTime();
            let diffYr = diffMs / MS_PER_YEAR;
            if (isLogTime)
              chartdata[i][key] = -Math.log10(diffYr);
            else
              chartdata[i][key] = -diffYr;
          }
        }
      }
    }

    // Find min and max value of x-axis
    minTime = Infinity;
    maxTime = -Infinity;
    for (let i = 0; i < chartdata.length; i++) {
      let dict = chartdata[i];
      for (let key in dict) {
        if (key.startsWith("time")) {
          if (chartdata[i][key] < minTime) {
            minTime = chartdata[i][key];
          }
          if (chartdata[i][key] > maxTime) {
            maxTime = chartdata[i][key];
          }
        }
      }
    }
    if (!isYBC) {  // XXX needed?
      minTime = minTime.getTime();
      maxTime = maxTime.getTime();
    }

    // anyQualitative = plotdata.data_is_qualitative.some(x => x);
    allQualitative = plotdata.data_is_qualitative.every(x => x);

    // Create divs inside <p id="chartstack"> that look like:
    // <div overflow="auto" class="row-md resizable_s" id="chartdiv" style="height:100px; border: 1px solid"></div>
    let charts = [];
    charts[nCharts - 1] = undefined;
    timeAxes[nCharts - 1] = undefined;
    valueAxes[nCharts - 1] = undefined;
    for (let i = nCharts - 1; i >= 0; i--) {
      let chartdiv = document.createElement("div");
      chartdiv.style.height = "300px";
      // chartdiv.style.border = "1px solid black";
      chartdiv.style.overflow = "hidden";
      chartdiv.id = "chartdiv" + i;
      chartdiv.className = "row-md resizable_s";
      // chartdiv.innerHTML = "Chart " + i;
      chartstack.appendChild(chartdiv);

      let chart = am4core.create(chartdiv.id, am4charts.XYChart);
      charts[i] = chart;
      chart.paddingLeft = 0;
    
      chart.data = chartdata;
      
      let timeAxis;
      if (isYBC) {
        timeAxis = chart.xAxes.push(new am4charts.ValueAxis());
      }
      else {
        timeAxis = chart.xAxes.push(new am4charts.DateAxis());
      } 
      timeAxes[i] = timeAxis;
      if (i == 0) {
        timeAxis.title.text = "Time";
      }

      // Location of the grid item within cell, 0: Start, 0.5: Middle, 1: End
      timeAxis.renderer.grid.template.location = 0.001;

      timeAxis.renderer.labels.template.location = 0.001;

      // timeAxis.renderer.minGridDistance = 30;

      // 0: Full first cell is shown, 0.5: Half of first cell is shown, 1: None of the first cell is visible
      timeAxis.startLocation = 0;

      // 0: None of the last cell is shown (don't do that), 0.5: Half of the last cell is shown, 1: Full last cell is shown 
      timeAxis.endLocation = 0.5;

      timeInterval = maxTime - minTime;
      timeAxis.min = minTime - timeInterval * 0.05;
      timeAxis.max = maxTime + timeInterval * 0.05;

      // XXX hard-coded timeUnit. Perhaps adjust based on time axis values?
      timeAxis.baseInterval = {
        "timeUnit": "minute",
        "count": 1
      };

      // timeAxis.layout = "none";

      timeAxis.events.on("startchanged", timeAxisChanged);  // Dragging the left limit
      timeAxis.events.on("endchanged", timeAxisChanged);  // Dragging the right limit

      // timeAxis.logarithmic = true;

      let valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
      valueAxes[i] = valueAxis;
      valueAxis.width = 40; // To get alignment for stacked charts

      const chart_is_qual = (is_stacked && plotdata.data_is_qualitative[i]) || allQualitative;

      if (chart_is_qual) {
        // Make this chart qualitative-type

        // timeAxis.renderer.grid.template.disabled = true;
        // timeAxis.renderer.labels.template.disabled = true;
        timeAxis.tooltip.disabled = true;

        valueAxis.min = -0.1;
        valueAxis.strictMinMax = true;
        valueAxis.renderer.grid.template.disabled = true;
        valueAxis.renderer.labels.template.disabled = true;
        valueAxis.renderer.baseGrid.disabled = true;
        valueAxis.tooltip.disabled = true;        
      }
      else {
      // if ((is_stacked && !plotdata.data_is_qualitative[i]) ||
      //     (!is_stacked && anyQuantitative)) {
        // Add legend (with legend names being series.name) 
        chart.legend = new am4charts.Legend();
        chart.legend.position = "bottom";
        chart.legend.halign = "mid";
        // chart.legend.width = 150;

      }

      // Add cursor
      chart.cursor = new am4charts.XYCursor();
      chart.cursor.behavior = "none";  // Disable zoom since difficult to get synced DateAxes for stacked plots
      if (chart_is_qual) {
        chart.cursor.lineY.disabled = true;
      }


      // Horizontal scrollbar (only to the bottom chart of stacked)
      if (!is_stacked || i == 0) {
        chart.scrollbarX = new am4core.Scrollbar();
        chart.scrollbarX.parent = chart.bottomAxesContainer;
        chart.scrollbarX.startGrip.icon.disabled = true;
        chart.scrollbarX.endGrip.icon.disabled = true;
        chart.scrollbarX.minHeight = 5;
      }

      // Vertical scrollbar
      if (!chart_is_qual) {
        chart.scrollbarY = new am4core.Scrollbar();
        chart.scrollbarY.parent = chart.leftAxesContainer;
        chart.scrollbarY.startGrip.icon.disabled = true;
        chart.scrollbarY.endGrip.icon.disabled = true;  
        chart.scrollbarY.minWidth = 5;    
        chart.scrollbarY.toBack();
      }

      // Add export menu (in top right corner of chart)
      chart.exporting.menu = new am4core.ExportMenu();

    }

    for (let i = 0; i < nTimelines; i++) {
      let series;
      if (is_stacked) {
        series = charts[i].series.push(new am4charts.LineSeries());        
      }
      else {
        series = charts[0].series.push(new am4charts.LineSeries());
      }
      series.name = plotdata.legends[i];
      // series.stroke = am4core.color("#CDA2AB");
      // series.strokeWidth = 3;
      // series.tensionX = 0.8;
      var circleBullet = series.bullets.push(new am4charts.CircleBullet());
      circleBullet.circle.radius = 2;

      series.connect = false;
      series.autoGapCount = Infinity;
      series.dataFields.valueY = "value" + i;
      if (isYBC) {
        series.dataFields.valueX = "time" + i;
      }
      else {
        series.dataFields.dateX = "time" + i;
      }
      series.dataItems.template.locations.dateX = 0;

      // if ((is_stacked || nTimelines === 1) && plotdata.data_is_qualitative[i]) {
      if (plotdata.data_is_qualitative[i]) {
        var labelBullet = series.bullets.push(new am4charts.LabelBullet());
        labelBullet.label.text = "{text" + i + "}";
        labelBullet.label.maxWidth = 150;
        labelBullet.label.wrap = true;
        labelBullet.label.truncate = false;
        labelBullet.label.textAlign = "middle";
        labelBullet.label.verticalCenter = "bottom";
        labelBullet.label.paddingTop = 20;
        labelBullet.label.paddingBottom = 20;
        labelBullet.label.fill = am4core.color("#999");

        circleBullet.setStateOnChildren = true;
        circleBullet.states.create("hover");
        circleBullet.circle.states.create("hover").properties.radius = 10;
        labelBullet.setStateOnChildren = true;
        labelBullet.states.create("hover").properties.scale = 1.1;
        labelBullet.label.states.create("hover").properties.fill = am4core.color("#000");
      }
    }

    $('.resizable_s').resizable({
      handles: 's'
    });

  }

  function timeAxisChanged(ev) {
    var start = ev.target.minZoomed;
    var end = ev.target.maxZoomed;
    for (let j = timeAxes.length - 1; j >= 1; j--) {  // All charts except the bottom
      timeAxes[j].min = start;
      timeAxes[j].max = end;
      timeAxes[j].strictMinMax = true;

      valueAxes[j].includeAllValues = false;
      // valueAxes[j].min = valueAxes[j].minZoomed;
      // valueAxes[j].max = valueAxes[j].maxZoomed;
      //valueAxes[j].strictMinMax = true;
    }

    

  }  

  // XXX disable and hide the checkbox
  // $("#xnode-0").hide();
  // $("#xnode-0").prop('disabled', true);

  // $("#treeview").hummingbird("expandAll");  // XXX temporary

  // To make enabling correct at reload
  toggle_time_unit_current_year();
});


function toggle_time_unit_current_year() {
  const time_unit = document.getElementById("time_unit");
  if (time_unit === null)
      return
  let selValue = time_unit.value;
  lbl = document.getElementById("label_current_year");
  lst = document.getElementById("input_current_year");
  // logCheck = document.getElementById("log_time_checkbox");
  // logLabel = document.getElementById("label_log_time_checkbox");
  logDiv = document.getElementById("log_time_div");
  
  if (selValue === "auto") {
    lbl.style.visibility = "hidden";
    lst.style.visibility = "hidden";

    // logLabel.style.display = "none";
    // logCheck.style.display = "none";
    logDiv.style.display = "none";


    /* To make them disappear altogether (and not even take up any space) */
    // lbl.style.display = "none";
    // lst.style.display = "none";
  }
  else {
    lbl.style.visibility = "visible";
    lst.style.visibility = "visible";
    // logLabel.style.display = "block";
    // logCheck.style.display = "block";
    logDiv.style.display = "block";

    /* To make them disappear altogether (and not even take up any space) */
    // lbl.style.display = "block";
    // lst.style.display = "block";
  }
  // alert(selValue);
}


function deleteNote(noteId) {
  fetch("/delete-note", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId }),
  }).then((_res) => {
    window.location.href = "/";
  });
}
