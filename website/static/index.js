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
    const CREATE = 'button-createscript';
    const DELETE = 'button-deletescript';
    const SAVE = 'button-savescript';
    
    const usersScripts = document.getElementById(USERSCRIPTS);
    const usersScriptName = document.getElementById(USERSCRIPT_NAME);
    const usersScriptCode = document.getElementById(USERSCRIPT_CODE);
    const exampleScripts = document.getElementById(EXAMPLESCRIPTS);
    const createButton = document.getElementById(CREATE);
    const deleteButton = document.getElementById(DELETE);
    const saveButton = document.getElementById(SAVE);

    class UIScript {
        constructor(id, name, code) {
            this.id = id;
            this.name = name
            this.code = code;
        }

        // set(id, name, code) {
        //     this.id = id;
        //     this.name = name;
        //     this.code = code;
        // }

        // setCurrent() {
        //     this.id = getSelectedUserScripts()[0];
        //     this.name = usersScriptName.value;
        //     this.code = usersScriptCode.value;    
        // }

        getName() {
            return this.name;
        }

        getCode() {
            return this.code;
        }

        // equals(name, code) {
        //     return (this.name === name && this.code === code);
        // }
    }

    // A dictionary of UIScript objects, keyed by id. For caching to avoid hitting the db so often
    var displayedScripts = {};
    function updateDisplayedScripts(id, name, code) {
        if (id in Object.entries(displayedScripts)) {
            displayedScripts[id].set(id, name, code);
        }
        else {
            displayedScripts[id] = new UIScript(id, name, code);
        }
    }

    /*
    To keep track of previously displayed script, to check whether or not that
    script need to be saved, by comparing with the cache.
    */
    var currentSelUserScripts = null;
    // var currentSettings = {USERSCRIPTS: null, USERSCRIPT_NAME: null, USERSCRIPT_CODE: null};
    // function updateCurrentSettings() {
    //     currentSettings[USERSCRIPTS] = getSelectedUserScripts();
    //     currentSettings[USERSCRIPT_NAME] = usersScriptName.value;
    //     currentSettings[USERSCRIPT_CODE] = usersScriptCode.value;
    // }
    // currentSettings = new UIScript();

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
        previousSelection = currentSelUserScripts;
        if (previousSelection) {
            if (previousSelection.length == 1) {
                // Compare cached version of previously displayed script
                // with currently displayed content. If not same, ask user
                // to save.
                msg = null;
                lastDisplayed = displayedScripts[previousSelection[0]];
                if (lastDisplayed.getName() != usersScriptName.value) {
                    const oldName = lastDisplayed.getName();
                    const newName = usersScriptName.value;
                    msg = `The name change from '${oldName}' to '${newName}' has not been saved.`;
                } 
                else if (lastDisplayed.getCode() != usersScriptCode.value) {
                    msg = `The code for '${lastDisplayed.getName()}' has not been saved.`;
                }
                if (msg) {
                    alert(msg);
                }
            }
        }

        currentSelUserScripts = getSelectedUserScripts();

        const selectedValues = getSelectedUserScripts();
        if (selectedValues.length != 1) {  // Multiple or empty selection or empty list
            // updateCurrentSettings();
            // currentSelUserScripts = getSelectedUserScripts();
            handleVisibility();            
            return;
        }
        const selectedValue = selectedValues[0];

        const get_url = "/get/" + selectedValue;  // XXX use Jinja2: {{ url_for("get") | tojson }}
        // const get_arg = {"method": "GET"};
        fetch(get_url)
            .then(response => response.json())
            .then(data => {
                const name = data['name'];
                const code = data['code'];
                usersScriptName.value = name;
                usersScriptCode.value = code;
                updateDisplayedScripts(selectedValue, name, code);
                // updateCurrentSettings();
                // currentSelUserScripts = getSelectedUserScripts();
                handleVisibility();
            });

    }

    /* Listener. */
    function exampleScriptsSelectionChanged() {
        const selectedValue = getSelectedExampleScript();
        const get_url = "/get_example/" + selectedValue;  // XXX use Jinja2: {{ url_for("get") | tojson }}
        fetch(get_url)
            .then(response => response.json())
            .then(data => {
                const name = data['name'];
                const code = data['code'];
                exampleScripts.value = code;
            });
    }

    function handleVisibility() {
        const nSelectedValues = getSelectedUserScripts().length;
        let showScript = (nSelectedValues == 1);
        if (!showScript) {
            usersScriptName.value = "";
            usersScriptCode.value = "";
        }
        const deleteScriptButton = deleteButton;
        if (deleteScriptButton) {
            let showDeleteScriptButton = (nSelectedValues >= 1);
            if (showDeleteScriptButton) {
                deleteScriptButton.style.display = "";
            }
            else {
                deleteScriptButton.style.display = "none";
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

    /* Listener. */
    function saveScriptButtonClicked() {
        const selectedValue = usersScripts.value;
        if (selectedValue.length == 0) {  // Empty selection or empty list
            return;
        }
        
        const name = usersScriptName.value;
        const code = usersScriptCode.value;
        const dataSend = {'id': selectedValue, 'name': name, 'code': code};

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
                    updateOptionInUsersScripts(selectedValue, name);
                    updateDisplayedScripts(selectedValue, name, code)
                }
            });
        
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


}
