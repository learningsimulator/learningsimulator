document.addEventListener("DOMContentLoaded", onLoad);

function onLoad() { // DOM is loaded and ready

    // Check that this is home.html
    homeDiv = document.getElementById('div-home');
    if (!homeDiv) {
        return;
    }

    const USERSCRIPT_CODE = 'textarea-code';
    const DEMOSCRIPT_CODE = 'textarea-code-demo';

    const usersScriptCode = document.getElementById(USERSCRIPT_CODE);
    const demoScriptCode = document.getElementById(DEMOSCRIPT_CODE);
    const usersScriptName = document.getElementById('input-scriptname');
    const demoScripts = document.getElementById('select-demoscripts');
    const saveButton = document.getElementById('button-savescript');
    const userRunButton = document.getElementById('button-run');
    const demoRunButton = document.getElementById('button-run-demo');
    const lineCounter = document.getElementById('linecounter');
    const errDlgDetailsButton = document.getElementById('button-errdlg-details');
    const errDlgDetails = document.getElementById('textarea-errdlg-details');
    const errDlgClose = document.getElementById("errdlg-close");
    const errorDlgModalBg = document.getElementById("div-errordlg-modal-bg");
    const errDlgMsg = document.getElementById("div-errmsg");
    const divDemo = document.getElementById("div-demo");
    const showDivDemoButton = document.getElementById("button-showdemo");
    
    // Settings
    const settingsButton = document.getElementById("button-settings");
    const settingsDlgModalBg = document.getElementById("div-settingsdlg-modal-bg");
    const settingsDlgOK = document.getElementById("settingsdlg-ok");
    const settingsDlgCancel = document.getElementById("settingsdlg-cancel");

    // Showing/hiding demo scripts
    showDivDemoButton.addEventListener("click", toggleDivDemo);
    function toggleDivDemo () {
        showDivDemoButton.classList.toggle("active");
        // var divDemo = this.nextElementSibling;
        if (divDemo.style.maxHeight) {
            divDemo.style.maxHeight = null;
        }
        else {
            divDemo.style.maxHeight = divDemo.scrollHeight + "px";
        } 
    }

    // To synchronise the scrolling of script textarea and linecounter textarea:
    if (usersScriptCode) {
        usersScriptCode.addEventListener('scroll', () => {
            lineCounter.scrollTop = usersScriptCode.scrollTop;
            lineCounter.scrollLeft = usersScriptCode.scrollLeft;
        });
    }

    // Enable the tab key to be input into the script textarea:
    if (usersScriptCode) {
        usersScriptCode.addEventListener('keydown', (e) => {
            let keyCode = e.key;
            const { value, selectionStart, selectionEnd } = usersScriptCode;
            if (keyCode === 'Tab') {
                e.preventDefault();
                usersScriptCode.value = value.slice(0, selectionStart) + '\t' + value.slice(selectionEnd);
                usersScriptCode.setSelectionRange(selectionStart + 1, selectionStart + 1)
            }
        });
    }

    // To output the line counter display:
    var lineCountCache = 0;
    function updateLineCounter() {
        const lineCount = usersScriptCode.value.split('\n').length;
        if (lineCountCache != lineCount) {
            var outarr = new Array();
            for (let x = 0; x < lineCount; x++) {
                outarr[x] = (x + 1) + '';
            }
            lineCounter.value = outarr.join('\n');
            lineCountCache = lineCount;
        }
    }
    if (usersScriptCode) {
        usersScriptCode.addEventListener('input', () => {  // Fires e.g. when pasting by drag-and-drop into the textarea
            updateLineCounter();
        });
    }


    // For resizing the resizable divs where the Plotly plots are rendered
    var chartDivResizeObserver = new ResizeObserver(entries => {
        if (entries.length > 1) {  // This is run once right after all observed divs are created
            return;
        }
        const entry = entries[0];
        const chartDiv = entry.target;
        const newWidth = chartDiv.clientWidth;
        const newHeight = chartDiv.clientHeight;
        const update = {
            width: newWidth,
            height: newHeight
        };
        Plotly.relayout(chartDiv, update);
    });

    // ======================================= Error "dialog box" =======================================
    errDlgDetailsButton.addEventListener('click', () => {
        if (errDlgDetails.style.display === "none") {
            errDlgDetails.style.display = "block";
            errDlgDetailsButton.textContent = "<< Details";
        }
        else {
            errDlgDetails.style.display = "none";
            errDlgDetailsButton.textContent = "Details >>";
        }
    });

    // When the user clicks on <span> (x), close the error dialog
    errDlgClose.onclick = function() {
        errorDlgModalBg.style.display = "none";
        usersScriptCode.focus();  // To see the selection of the failing line
    }

    // When the user clicks anywhere outside of the modal, close it
    // window.onclick = function(event) {
    //     if (event.target == errorDlgModalBg) {
    //         errorDlgModalBg.style.display = "none";
    //     }
    // }
    // ==================================================================================================

    class Settings {
        constructor() {
            this.graph_lib = null;
            this.plot_orientation = null;
            this.plot_width = null;
            this.plot_height = null;
            this.legend_x = null;
            this.legend_y = null;
            this.legend_x_anchor = null;
            this.legend_y_anchor = null;
            this.legend_orientation = null;
            this.paper_color = null;
            this.plot_bgcolor = null;
            this.mplpdf = null;
            this.keep_plots = null;

            // Read values from db

            // The id of the settings for the current user is stored in the
            // attribute "data-settingsid" of the textbox
            const settingsId = usersScriptCode.dataset.settingsid;

            const get_url = "/get_settings/" + settingsId;  // XXX use Jinja2: {{ url_for("get") | tojson }}
            fetch(get_url)
                .then(response => response.json())
                .then(data => {
                    this.graph_lib = data['graph_lib'];
                    this.plot_orientation = data['plot_orientation'];
                    this.plot_width = data['plot_width'];
                    this.plot_height = data['plot_height'];
                    this.legend_x = data['legend_x'];
                    this.legend_y = data['legend_y'];
                    this.legend_x_anchor = data['legend_x_anchor'];
                    this.legend_y_anchor = data['legend_y_anchor'];
                    this.legend_orientation = data['legend_orientation'];
                    this.paper_color = data['paper_color'];
                    this.plot_bgcolor = data['plot_bgcolor'];
                    this.mplpdf = data['mplpdf'];
                    this.keep_plots = data['keep_plots'];
                }
            );
        }

        validate() {
            let err = null;
            return err;
        }

        save() {
            this.graph_lib = document.getElementById("settings-graphlib").value;
            this.plot_orientation = document.getElementById("settings-plotorientation").value;
            this.plot_width = document.getElementById("settings-plotwidth").value;
            this.plot_height = document.getElementById("settings-plotheight").value;
            this.legend_x = document.getElementById("settings-legendrelx").value;
            this.legend_y = document.getElementById("settings-legendrely").value;
            this.legend_x_anchor = document.getElementById("settings-legendanchorx").value;
            this.legend_y_anchor = document.getElementById("settings-legendanchory").value;
            this.legend_orientation = document.getElementById("settings-legendorientation").value;
            this.paper_color = document.getElementById("settings-paperbgcolor").value;
            this.plot_bgcolor = document.getElementById("settings-plotbgcolor").value;
            this.mplpdf = document.getElementById("settings-mplpdf").checked;
            this.keep_plots = document.getElementById("settings-keep").checked;

            // Save to db
            return this.writeToDB();;
        }

        writeToDB() {
            // The id of the settings for the current user is stored in the
            // attribute "data-settingsid" of the textbox
            const settingsId = usersScriptCode.dataset.settingsid;

            const dataSend = {'id': settingsId, 'settings': this};
            const save_url = "/save_settings";  // XXX use Jinja2: {{ url_for("save") | tojson }}
            const save_arg = {"method": "POST",
                              "headers": {"Content-Type": "application/json"},
                              "body": JSON.stringify(dataSend)};
            fetch(save_url, save_arg)
                .then(response => response.json())
                .then(data => {
                    const error = data['error'];
                    if (error) {
                        return error;
                    }
                    else {
                        return null;
                    }
                }
            );
        }

        update_ui() {
            document.getElementById("settings-graphlib").value = this.graph_lib;
            document.getElementById("settings-plotorientation").value = this.plot_orientation;
            document.getElementById("settings-plotwidth").value = this.plot_width;
            document.getElementById("settings-plotheight").value = this.plot_height;
            document.getElementById("settings-legendrelx").value = this.legend_x;
            document.getElementById("settings-legendrely").value = this.legend_y;
            document.getElementById("settings-legendanchorx").value = this.legend_x_anchor;
            document.getElementById("settings-legendanchory").value = this.legend_y_anchor;
            document.getElementById("settings-legendorientation").value = this.legend_orientation;
            document.getElementById("settings-paperbgcolor").value = this.paper_color;
            document.getElementById("settings-plotbgcolor").value = this.plot_bgcolor;
            document.getElementById("settings-mplpdf").checked = this.mplpdf;
            document.getElementById("settings-keep").checked = this.keep_plots;
        }

    }

    var settings = new Settings();

    // ======================================= Settings "dialog box" =======================================

    // Open settings "dialog"
    if (settingsButton) {
        settingsButton.addEventListener('click', () => {
            settings.update_ui();
            settingsDlgModalBg.style.display = "block";
        });
    }

    // When the user clicks on Cancel, close the settings dialog
    settingsDlgCancel.onclick = function() {
        settingsDlgModalBg.style.display = "none";
    }

    if (settingsDlgOK) {
        settingsDlgOK.onclick = function() {
            const err_client = settings.validate();
            if (err_client) {
                alert(err_client);
                return;
            }        
            const err_server = settings.save();
            if (err_server) {
                alert(err_server);
                return;
            }
            else {
                settingsDlgModalBg.style.display = "none";
            }
        }
    }

    // When the user clicks anywhere outside of the modal, close it
    // window.onclick = function(event) {
    //     if (event.target == errorDlgModalBg) {
    //         errorDlgModalBg.style.display = "none";
    //     }
    // }
    // ==================================================================================================

    class UIScript {
        constructor(id, name, code) {
            this.set(id, name, code);
        }

        set(id, name, code) {
            this.id = id;
            this.name = name
            this.code = code;
        }

        getName() {
            return this.name;
        }

        getCode() {
            return this.code;
        }
    }

    // A dictionary of UIScript objects, keyed by id. For caching to avoid hitting the db so often
    var cachedScripts = {};
    function updateCachedScripts(id, name, code) {
        if (Object.hasOwn(cachedScripts, id)) {
            cachedScripts[id].set(id, name, code);
        }
        else {
            cachedScripts[id] = new UIScript(id, name, code);
        }
    }

    // Set event listener to button for running script
    if (userRunButton) {  // This button is only displayed when logged in
        userRunButton.addEventListener('click', userRunButtonClicked);
    }

    // Set event listener to button for running demo script
    demoRunButton.addEventListener('click', demoRunButtonClicked);

    // Set event listener to button for saving script
    if (saveButton) {
        saveButton.addEventListener('click', saveScriptButtonClicked);
    }

    // Set event listener to "Demo scripts" list
    demoScripts.addEventListener('change', demoScriptsSelectionChanged);


    /* Get the current sleection in the users scripts list. */
    function getSelectedDemoScript() {
        return demoScripts.value;
    }

    /* Listener. */
    function demoScriptsSelectionChanged() {
        const selectedValue = getSelectedDemoScript();
        const get_url = "/get_demo/" + selectedValue;  // XXX use Jinja2: {{ url_for("get") | tojson }}
        fetch(get_url)
            .then(response => response.json())
            .then(data => {
                const code = data['code'];
                demoScriptCode.value = code;
            }
        );
    }

    function saveScript(name, code) {
        const id = usersScriptCode.dataset.scriptid;  // The id of the current script is stored in the attribute "data-scriptid" of the textbox
        const dataSend = {'id': id, 'name': name, 'code': code};
        const save_url = "/save";  // XXX use Jinja2: {{ url_for("save") | tojson }}
        const save_arg = {"method": "POST",
                          "headers": {"Content-Type": "application/json"},
                          "body": JSON.stringify(dataSend)};
        fetch(save_url, save_arg)
            .then(response => response.json())
            .then(data => {
                const error = data['error'];
                if (error) {
                    alert(error);
                }
            }
        );
    }

    /* Listener. */
    function saveScriptButtonClicked() {
        const name = usersScriptName.value;
        const code = usersScriptCode.value;
        saveScript(name, code);
    }

    function userRunButtonClicked() {
        runButtonClicked(USERSCRIPT_CODE, "plotarea");
    }

    function demoRunButtonClicked() {
        runButtonClicked(DEMOSCRIPT_CODE, "plotarea-demo");
    }

    function runButtonClicked(textareaID, divID) {
        const code = document.getElementById(textareaID).value;
        const dataSend = {'code': code};
        const isMpl = (settings.graph_lib === "mpld3");
        let run_url;
        if (isMpl) {
            run_url = "/run_mpl_fig";  // XXX use Jinja2: {{ url_for("run_mpl") | tojson }}
        }
        else {
            run_url = "/run";  // XXX use Jinja2: {{ url_for("run") | tojson }}
        }
        const run_arg = {"method": "POST",
                         "headers": {"Content-Type": "application/json"},
                         "body": JSON.stringify(dataSend)};
        fetch(run_url, run_arg)
            .then(response => response.json())
            .then(data => {
                if (Object.hasOwn(data, 'err_msg')) {
                    if (data.lineno) {
                        selectLine(data.lineno);
                    }
                    displayRunError(data);
                    return;
                }
                try {
                    if (isMpl)
                        postproc_mpl_fig(data, divID);
                    else {
                        postproc(data, divID);
                    }
                }
                catch (err) {
                    alert(err);
                }
            });
    }

    function displayRunError(data) {
        errDlgMsg.textContent = data.err_msg;
        errDlgDetails.value = data.stack_trace;
        errDlgDetails.style.display = "none";
        errDlgDetailsButton.textContent = "Details >>"
        errorDlgModalBg.style.display = "block";
    }

    function selectLine(lineNo) {
        const code = usersScriptCode.value;
        const lines = code.split('\n');
        const nLines = lines.length;
        if (lineNo <= nLines) {
            let selectionStart;
            let selectionEnd;
            if (lineNo === 1) {
                selectionStart = 0;
            }
            else {
                selectionStart = code.split('\n', lineNo - 1).join('\n').length + 1;
            }
            if (lineNo === nLines) {
                selectionEnd = code.length;
            }
            else {
                selectionEnd = code.split('\n', lineNo).join('\n').length;
            }

            // Highlight the line
            usersScriptCode.focus();
            usersScriptCode.setSelectionRange(selectionStart, selectionEnd);

            // Extra luxury: Try to scroll to make the highlighted line visible
            // XXX: Seems to make line counter off
            // try {
            //     const lineHeight = parseInt(getComputedStyle(usersScriptCode).lineHeight);
            //     usersScriptCode.scrollTop = (lineNo - 1) * lineHeight;
            //     lineCounter.scrollTop = (lineNo - 1) * lineHeight;
            // }
            // catch (error) {  // Do nothing
            // }
        }
    }

// =================================================================================
// PLOTTING
// =================================================================================

    function postproc(postcmds, plotlyDivID) {
        let plotArea = document.getElementById(plotlyDivID);
        removeAllChartDivs(plotlyDivID);
        let currSubplot = null;
        let collectingSubplots = false;
        let createSubplotLegend = false;
        let collectedSubplots = [];
        let currFig = null;
        for (let i = 0; i < postcmds.length; i++)  {
            let cmd = postcmds[i];
            let createSubplots = false;
            let createFigure = false;
            const type = cmd['type'];
            if (type === 'figure') {
                currFig = cmd;
                createFigure = true;
            }
            else if (type === 'subplot') {
                currSubplot = cmd;
                createFigure = (currFig === null);
                collectingSubplots = true;
            }
            else if (type === 'plot') {
                createFigure = (currFig === null && currSubplot === null);
                if (collectingSubplots) {
                    let plotArgs = getPlotArgs(cmd, currFig);
                    plotArgs['subplot'] = currSubplot;
                    collectedSubplots.push(plotArgs);
                }

                createSubplots = collectingSubplots && isLastPlotForSubplot(postcmds, i);
                if (createSubplots) {
                    collectingSubplots = false;
                }
            }

            if (createFigure) {
                let chartDiv = document.createElement('div');
                // let chartHr = document.createElement('hr');
                chartDiv.dataset.containsPlot = "0";
                chartDiv.dataset.title = "";
                currFig = chartDiv;
                // chartdiv.style.height = "300px";
                chartDiv.style.resize = "both";
                chartDiv.style.overflow = "hidden";
                chartDiv.style.border = "3px solid green";
                chartDivResizeObserver.observe(chartDiv);

                plotArea.appendChild(chartDiv);
                // plotArea.appendChild(chartHr);
                createSubplotLegend = false;
            }

            if (type === 'plot') {
                if (!collectingSubplots) {
                    if (createSubplots) {
                        plotSubplots(currFig, collectedSubplots);
                        if (createSubplotLegend) {
                            Plotly.relayout(currFig, {showlegend: true});
                        }
                        collectedSubplots = [];
                    }
                    else {
                        const plotArgs = getPlotArgs(cmd, currFig);
                        plot(currFig, plotArgs);
                    }
                    currFig.dataset.containsPlot = "1";
                }
            }
            else if (type === 'legend') {
                if (currFig !== null) {  // If null, @legend is before @figure
                    if (!collectingSubplots && currFig.dataset.containsPlot === "1") {  // If "0", @legend is before @plot
                        Plotly.relayout(currFig, {showlegend: true});
                    }
                    else {
                        createSubplotLegend = true;
                    }
                }
            }
            else if (type === 'figure') {
                currFig.dataset.title = cmd['title'];
            }
        }
    }

    // function postproc_mpl(data, divID) {
    //     let plotArea = document.getElementById(divID);
    //     removeAllChartDivs(divID);
    //     for (let i = 0; i < data.length; i++)  {
    //         let chartDiv = document.createElement('div');
    //         chartDiv.id = "div-mpld3_" + i;
    //         currFig = chartDiv;
    //         chartDiv.style.resize = "both";
    //         chartDiv.style.overflow = "hidden";
    //         chartDiv.style.border = "3px solid blue";
    //         plotArea.appendChild(chartDiv);
    //         Function(data[i])();  // Better than "eval(data[i])""
    //     }
    // }

    function postproc_mpl_fig(figImgs, divID) {
        let plotArea = document.getElementById(divID);
        removeAllChartDivs(divID);
        for (let i = 0; i < figImgs.length; i++)  {
            let chartDiv = document.createElement('div');
            chartDiv.id = "div-mpld3_" + i;
            chartDiv.style.border = "3px solid blue";

            let chartImg = document.createElement('img');
            chartImg.setAttribute("src", figImgs[i]);
            chartImg.setAttribute("alt", "Matplotlib chart");
            chartDiv.appendChild(chartImg);

            plotArea.appendChild(chartDiv);
        }
    }

    function plotSubplots(chartDiv, subplotPlots) {
        let nRows;
        let nCols;
        let layout = {...subplotPlots[0]['layout']};  // Copy of first subplotplot
        let traces = [];
        for (plotCmd of subplotPlots) {
            const subplotSpec = JSON.parse(plotCmd['subplot']['spec_list']);
            const mpl_prop = JSON.parse(plotCmd['subplot']['mpl_prop']);
            
            nRows = subplotSpec[0];
            nCols = subplotSpec[1];
            const subplotNo = subplotSpec[2];
            for (let line of plotCmd['plotlyData']) {
                line['xaxis'] = 'x' + subplotNo;
                line['yaxis'] = 'y' + subplotNo;
                traces.push(line);
            }
            let xaxis = {};
            if (Object.hasOwn(mpl_prop, 'xlim')) {
                xaxis.range = mpl_prop['xlim'];
            }
            if (Object.hasOwn(mpl_prop, 'xlabel')) {
                xaxis.title = {text: mpl_prop['xlabel']};
            }
            layout['xaxis' + subplotNo] = xaxis;

            let yaxis = {};
            if (Object.hasOwn(mpl_prop, 'ylim')) {
                yaxis.range = mpl_prop['ylim'];
            }
            if (Object.hasOwn(mpl_prop, 'ylabel')) {
                yaxis.title = {text: mpl_prop['ylabel']};
            }
            layout['yaxis' + subplotNo] = yaxis;

        }
        // let gridSubplots = [];
        // let cnt = 1;
        // for (let col = 0; col < nCols; col++) {
        //     let gridCol = [];
        //     for (let row = 0; row < nRows; row++) {
        //         gridCol.push('x' + cnt + 'y' + cnt);
        //         cnt++;
        //     }
        //     gridSubplots.push(gridCol);
        // }
        const grid = {'rows': nRows,
                      'columns': nCols,
                    //   'subplots': gridSubplots};
                      'pattern': 'independent'};
        layout['grid'] = grid;
        plot(chartDiv, {'plotlyData': traces, 'layout': layout});
    }

    function isLastPlotForSubplot(postcmds, ind) {
        if (ind === postcmds.length - 1) {
            return true;
        }
        for (let i = ind + 1; i < postcmds.length; i++) {
            const cmd = postcmds[i];
            if (cmd['type'] === 'plot') {
                return false;
            }
            else if (cmd['type'] === 'figure') {
                return true;
            }
            else if (cmd['type'] === 'subplot') {
                return false;
            }
        }
        return true;
    }

    function getPlotArgs(cmd, chartDiv) {
        const ydatas = JSON.parse(cmd['ydatas']);
        const nLines = ydatas.length;        
        plot_argss = JSON.parse(cmd['plot_args']);

        let plotlyData = [];
        for (let i = 0; i < nLines; i++)  {
            const ydata = ydatas[i];
            const plot_args = plot_argss[i];
            const N = ydata.length;

            // Create xdata = [1, 2, 3, ..., N]
            let xdata = [];
            for (let i = 1; i <= N; i++) {
                xdata.push(i);
            }

            // label
            let plotlyLabel = plot_args['label'];

            // linewidth, color
            let plotlyLineprops = {};
            if (plot_args['linewidth']) {
                plotlyLineprops['width'] = plot_args['linewidth'];
            }
            if (plot_args['color']) {
                plotlyLineprops['color'] = plot_args['color'];
            }

            // marker, markersize
            let plotlyMarker = {};
            let plotlyMode = 'lines';
            if (plot_args['marker']) {
                plotlyMarker['symbol'] = plot_args['marker'];
                plotlyMode = 'lines+markers';
                if (plot_args['markersize']) {
                    plotlyMarker['size'] = plot_args['markersize'];
                }
            }

            let line = {
                x: xdata,
                y: ydata,
                type: 'line',
                mode: plotlyMode,
                name: plotlyLabel,
                line: plotlyLineprops,
                marker: plotlyMarker
            };
            plotlyData.push(line);
        }
        let layout = {
            showlegend: false,
            // plot_bgcolor: '#444',
            paper_bgcolor: '#eee',
            title: chartDiv.dataset.title            
            // xaxis: {  // XXX remember that for subplots, the axes are called xaxis2, etc.
            //     zeroline: true,
            //     zerolinewidth: 1,
            //     zerolinecolor: 'black'
            // },
            // yaxis: {
            //     zeroline: true,
            //     zerolinewidth: 1,
            //     zerolinecolor: 'red'
            // },
        };
        return {'plotlyData': plotlyData, 'layout': layout};
    }

    function plot(chartDiv, plotArgs) {
        const plotlyData = plotArgs['plotlyData'];
        const layout = plotArgs['layout'];
        if (chartDiv.dataset.containsPlot === "1") {
            Plotly.addTraces(chartDiv, plotlyData);    
        }
        else {
            Plotly.react(chartDiv, plotlyData, layout);
            // Plotly.newPlot(chartDiv, plotlyData, layout);
        }
    }

    function removeAllChartDivs(plotlyDivID) {
        // Plotly.purge("plotarea");
        Plotly.purge(plotlyDivID);
        let plotArea = document.getElementById(plotlyDivID);
        while (plotArea.firstChild) {
            plotArea.removeChild(plotArea.lastChild);
        }
    }
      

}
