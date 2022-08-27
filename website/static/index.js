document.addEventListener("DOMContentLoaded", onLoad);

function onLoad() { // DOM is loaded and ready

    // Check that this is home.html
    homeDiv = document.getElementById('div-home');
    if (!homeDiv) {
        return;
    }

    const USERSCRIPTS = 'select-userscripts';
    const USERSCRIPT_NAME = 'input-scriptname';
    const USERSCRIPT_CODE = 'textarea-code';
    const EXAMPLESCRIPTS = 'select-examplescripts';
    const EXAMPLESCRIPTS_CODE = 'textarea-code-example';
    const CREATE = 'button-createscript';
    const DELETE = 'button-deletescript';
    const SAVE = 'button-savescript';
    const USER_RUN = 'button-run';

    const usersScripts = document.getElementById(USERSCRIPTS);
    const usersScriptName = document.getElementById(USERSCRIPT_NAME);
    const usersScriptCode = document.getElementById(USERSCRIPT_CODE);
    const exampleScripts = document.getElementById(EXAMPLESCRIPTS);
    const exampleScriptCode = document.getElementById(EXAMPLESCRIPTS_CODE);
    const createButton = document.getElementById(CREATE);
    const deleteButton = document.getElementById(DELETE);
    const saveButton = document.getElementById(SAVE);
    const userRunButton = document.getElementById(USER_RUN);
    const plotArea = document.getElementById("plotarea");

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

    /*
    To keep track of previously displayed script, to check whether or not that
    script need to be saved, by comparing with the cache.
    */
    var currentSelUserScripts = null;

    // Set event listener to "My scripts" list
    usersScripts.addEventListener('change', userScriptsSelectionChanged);

    // Set event listener to button for creating new script
    if (createButton) {  // This button is only displayed when logged in
        createButton.addEventListener('click', newScriptButtonClicked);
    }

    // Set event listener to button for deleting script
    if (deleteButton) {  // This button is only displayed when logged in
        deleteButton.addEventListener('click', deleteScriptButtonClicked);
    }

    // Set event listener to button for deleting script
    if (userRunButton) {  // This button is only displayed when logged in
        userRunButton.addEventListener('click', userRunButtonClicked);
    }

    // Set event listener to button for saving script
    saveButton.addEventListener('click', saveScriptButtonClicked);

    // Set event listener to "Example scripts" list
    exampleScripts.addEventListener('change', exampleScriptsSelectionChanged);

    handleVisibility();


    /* Get the current sleection in the users scripts list. */
    function getSelectedUserScripts() {
        return Array.from(usersScripts.querySelectorAll("option:checked"), e => e.value);
    }

    /* Get the current sleection in the users scripts list. */
    function getSelectedExampleScript() {
        return exampleScripts.value;
    }

    /* Listener. */
    function userScriptsSelectionChanged() {
        const previousSelection = currentSelUserScripts;
        if (previousSelection && previousSelection.length == 1) {
            // Compare cached version of previously displayed script
            // with currently displayed content. If not same, ask user
            // to save.
            askUser = false;
            msg = null;

            if (Object.hasOwn(cachedScripts, previousSelection[0])) {  // If selecting in list quickly, cachedScripts
                                                                       // may not have been updated wrt last selection
                                                                       // before this line is reached
                lastDisplayed = cachedScripts[previousSelection[0]];
                if (lastDisplayed.getName() != usersScriptName.value) {
                    askUser = true;
                    const oldName = lastDisplayed.getName();
                    const newName = usersScriptName.value;
                    msg = `The name change from '${oldName}' to '${newName}' has not been saved. ` +
                        "Do you want to save?";
                }
                else if (lastDisplayed.getCode() != usersScriptCode.value) {
                    askUser = true;
                    msg = `The code for '${lastDisplayed.getName()}' has not been saved. ` + 
                        "Do you want to save?";
                }
                if (askUser) {
                    const doSave = confirm(msg);
                    if (doSave) {
                        saveScript(previousSelection[0], usersScriptName.value, usersScriptCode.value);
                    }
                    else {
                        usersScripts.value = previousSelection;
                        return;
                    }
                }

            }
        }

        currentSelUserScripts = getSelectedUserScripts();
        const selectedValues = currentSelUserScripts;

        if (selectedValues.length != 1) {  // Multiple or empty selection or empty list
            handleVisibility();
            return;
        }
        const selectedValue = selectedValues[0];

        // Use cache if possible - otherwise fetch from database on sever
        if (Object.hasOwn(cachedScripts, selectedValue)) {
            const name = cachedScripts[selectedValue].getName();
            const code = cachedScripts[selectedValue].getCode();
            usersScriptName.value = name;
            usersScriptCode.value = code;
            handleVisibility();
        }
        else {
            const get_url = "/get/" + selectedValue;  // XXX use Jinja2: {{ url_for("get") | tojson }}
            fetch(get_url)
                .then(response => response.json())
                .then(data => {
                    const name = data['name'];
                    const code = data['code'];
                    usersScriptName.value = name;
                    usersScriptCode.value = code;
                    updateCachedScripts(selectedValue, name, code);
                    handleVisibility();
                });
            }
    }

    /* Listener. */
    function exampleScriptsSelectionChanged() {
        const selectedValue = getSelectedExampleScript();
        const get_url = "/get_example/" + selectedValue;  // XXX use Jinja2: {{ url_for("get") | tojson }}
        fetch(get_url)
            .then(response => response.json())
            .then(data => {
                const code = data['code'];
                exampleScriptCode.value = code;
            });
    }

    function handleVisibility() {
        const nSelectedValues = getSelectedUserScripts().length;
        const showScript = (nSelectedValues == 1);
        if (!showScript) {
            usersScriptName.value = "";
            usersScriptCode.value = "";
        }
        if (deleteButton) {
            const showDeleteButton = (nSelectedValues >= 1);
            if (showDeleteButton) {
                deleteButton.style.display = "";
            }
            else {
                deleteButton.style.display = "none";
            }
        }
        if (saveButton) {
            const showSaveButton = (nSelectedValues == 1);
            if (showSaveButton) {
                saveButton.style.display = "";
            }
            else {
                saveButton.style.display = "none";
            }
        }
        if (userRunButton) {
            const showRunButton = (nSelectedValues == 1);
            if (showRunButton) {
                userRunButton.style.display = "";
            }
            else {
                userRunButton.style.display = "none";
            }
        }

    }

    /* Utility. */
    function intToTwoNumberString(x) {
        let xStr = x + "";  // Add "" to convert to string
        if (xStr.length == 1) {
            xStr = "0" + xStr;
        }
        return xStr;
    }

    /* Utility. */
    function getNewScriptName() {
        let currentNames = [];
        for (var option of usersScripts.options) {
            currentNames.push(option.text);
        }
        let n = 1;
        let suggestedName;
        while (true) {
            suggestedName = "MyScript" + n;
            if (currentNames.indexOf(suggestedName) < 0) {
                break;
            }
            else {
                n = n + 1;
            }
        }
        return suggestedName;
    }

    function addOptionToUsersScripts(text, value) {
        let option = document.createElement("option");
        option.text = text;
        option.value = value;
        usersScripts.appendChild(option);
    }

    function removeOptionFromUsersScripts(value) {
        for (var i = 0; i < usersScripts.length; i++) {
            if (usersScripts.options[i].value == value) {
                usersScripts.remove(i);
                break;
            }
        }
    }

    function updateOptionInUsersScripts(value, name) {
        for (var i = 0; i < usersScripts.length; i++) {
            if (usersScripts.options[i].value == value) {
                usersScripts.options[i].text = name;
                break;
            }
        }
    }

    function saveScript(id, name, code) {
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
                else {
                    updateOptionInUsersScripts(id, name);
                    updateCachedScripts(id, name, code)
                }
            });
    }

    /* Listener. */
    function saveScriptButtonClicked() {
        const selectedValue = usersScripts.value;
        if (selectedValue.length == 0) {  // Empty selection or empty list
            return;
        }
        const name = usersScriptName.value;
        const code = usersScriptCode.value;
        saveScript(selectedValue, name, code);
    }

    /* Listener. */
    function deleteScriptButtonClicked() {
        const selectedValues = getSelectedUserScripts();
        if (selectedValues.length == 0) {  // Empty selection or empty list
            return;
        }

        const dataSend = {'ids': selectedValues};
        const delete_url = "/delete";  // XXX use Jinja2: {{ url_for("delete") | tojson }}
        const delete_arg = {"method": "POST",
                            "headers": {"Content-Type": "application/json"},
                            "body": JSON.stringify(dataSend)};
        fetch(delete_url, delete_arg)
            .then(response => response.json())
            .then(data => {
                const error = data['error'];
                if (error) {
                    alert(error);
                }
                else {
                    for (let selectedValue of selectedValues) {
                        removeOptionFromUsersScripts(selectedValue);
                    }
                }
                handleVisibility();
            });
    }

    /* Listener. */
    function newScriptButtonClicked() {
        const today = new Date();
        const monthStr = intToTwoNumberString(today.getMonth() + 1);
        const dateStr = intToTwoNumberString(today.getDate());
        const timeStr = intToTwoNumberString(today.getHours()) + ":" +
                        intToTwoNumberString(today.getMinutes()) + ":" +
                        intToTwoNumberString(today.getSeconds());
        const fullDateStr = today.getFullYear() + "-" + monthStr + "-" + dateStr + ", " + timeStr;

        const newScriptName = getNewScriptName();
        const newScriptCode = "# Learning simulator script\n# Created " + fullDateStr;
        const dataSend = {'name': newScriptName, 'code': newScriptCode};

        const add_url = "/add";  // XXX use Jinja2: {{ url_for("add") | tojson }}
        const add_arg = {"method": "POST",
                         "headers": {"Content-Type": "application/json"},
                         "body": JSON.stringify(dataSend)};

        fetch(add_url, add_arg)
            .then(response => response.json())
            .then(data => {
                const newScriptValue = data['id'];
                addOptionToUsersScripts(newScriptName, newScriptValue);
            });

    }

    function userRunButtonClicked() {
        const code = usersScriptCode.value;
        const dataSend = {'code': code};
        const run_url = "/run";  // XXX use Jinja2: {{ url_for("run") | tojson }}
        const run_arg = {"method": "POST",
                         "headers": {"Content-Type": "application/json"},
                         "body": JSON.stringify(dataSend)};
        fetch(run_url, run_arg)
            .then(response => response.json())
            .then(data => {
                postproc(data);
            });
    }


// =================================================================================
// PLOTTING
// =================================================================================

    function postproc(postcmds) {
        removeAllChartDivs();
        let currSubplot = null;
        let collectingSubplots = false;
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
                let chartHr = document.createElement('hr');
                chartDiv.dataset.containsPlot = "0";
                chartDiv.dataset.title = "";
                currFig = chartDiv;
                // chartdiv.style.height = "300px";
                plotArea.appendChild(chartDiv);
                plotArea.appendChild(chartHr);
            }

            if (type === 'plot') {
                if (!collectingSubplots) {
                    if (createSubplots) {
                        plotSubplots(currFig, collectedSubplots);
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
                alert("Doing the legend thing");
                Plotly.relayout(currFig, {showlegend: true});
            }
            else if (type === 'figure') {
                currFig.dataset.title = cmd['title'];
            }
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
            if (Object.hasOwn(mpl_prop, 'xlim')) {
                layout['xaxis' + subplotNo] = {range: mpl_prop['xlim']};
            }
            if (Object.hasOwn(mpl_prop, 'ylim')) {
                layout['yaxis' + subplotNo] = {range: mpl_prop['ylim']};
            } 
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
                mode: plotlyMode,
                name: plotlyLabel,
                line: plotlyLineprops,
                marker: plotlyMarker
            };
            plotlyData.push(line);
        }
        const layout = {
            showlegend: false,
            title: chartDiv.dataset.title
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

    function removeAllChartDivs() {
        Plotly.purge("plotarea");
        while (plotArea.firstChild) {
            plotArea.removeChild(plotArea.lastChild);
        }
    }
      

}
