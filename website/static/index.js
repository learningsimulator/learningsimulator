document.addEventListener("DOMContentLoaded", onLoad);

function onLoad() { // DOM is loaded and ready

    // Check that this is home.html
    homeDiv = document.getElementById('div-home');
    if (!homeDiv) {
        return;
    }

    // Set event listener to "My scripts" list
    const myScriptsSelect = document.getElementById('select-myscripts');
    myScriptsSelect.addEventListener('change', myScriptsSelectionChanged);

    // Set event listener to button for creating new script
    const newScriptButton = document.getElementById('button-newscript');
    if (newScriptButton) {  // This button is only displayed when logged in
        newScriptButton.addEventListener('click', newScriptButtonClicked);
    }

    // Set event listener to button for deleting script
    const deleteScriptButton = document.getElementById('button-deletescript');
    if (deleteScriptButton) {  // This button is only displayed when logged in
        deleteScriptButton.addEventListener('click', deleteScriptButtonClicked);
    }

    // Set event listener to button for saving script
    const saveScriptButton = document.getElementById('button-savescript');
    saveScriptButton.addEventListener('click', saveScriptButtonClicked);

    handleEmptySelection();

    /* Listener. */
    function myScriptsSelectionChanged() {
        const selectedValue = myScriptsSelect.value;

        const get_url = "/get/" + selectedValue;  // XXX use Jinja2: {{ url_for("get") | tojson }}
        const get_arg = {"method": "GET"};
        fetch(get_url, get_arg)
            .then(response => response.json())
            .then(data => {
                const name = data['name'];
                const code = data['code'];
                document.getElementById('input-scriptname').value = name;
                document.getElementById('textarea-code').value = code;
                handleEmptySelection();
            });
                
    }


    function handleEmptySelection() {
        var scriptDiv = document.getElementById('div-script');
        const selectedValue = myScriptsSelect.value;
        // alert("deleteScriptButton.style.display: " + deleteScriptButton.style.display);
        if (selectedValue.length == 0) {  // Empty selection or empty list
            scriptDiv.style.display = "none";
            if (deleteScriptButton) {
                deleteScriptButton.style.display = "none";
            }
        }
        else {
            scriptDiv.style.display = "block";
            if (deleteScriptButton) {
                deleteScriptButton.style.display = "";
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
        for (var option of myScriptsSelect.options) {
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

    function addOptionToMyScriptsSelect(text, value) {
        let option = document.createElement("option");
        option.text = text;
        option.value = value;
        myScriptsSelect.appendChild(option);
    }

    function removeOptionFromMyScriptsSelect(value) {
        for (var i = 0; i < myScriptsSelect.length; i++) {
            if (myScriptsSelect.options[i].value == value) {
                myScriptsSelect.remove(i);
                break;
            }
        }
    }

    function updateOptionInMyScriptsSelect(value, name) {
        for (var i = 0; i < myScriptsSelect.length; i++) {
            if (myScriptsSelect.options[i].value == value) {
                myScriptsSelect.options[i].text = name;
                break;
            }
        }
    }

    /* Listener. */
    function saveScriptButtonClicked() {
        const selectedValue = myScriptsSelect.value;
        if (selectedValue.length == 0) {  // Empty selection or empty list
            return;
        }
        
        const newScriptName = document.getElementById('input-scriptname').value;
        const newScriptContents = document.getElementById('textarea-code').value;
        const dataSend = {'id': selectedValue, 'name': newScriptName, 'code': newScriptContents};

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
                    updateOptionInMyScriptsSelect(selectedValue, newScriptName);
                }
            });
        
    }

    /* Listener. */
    function deleteScriptButtonClicked() {
        const selectedValue = myScriptsSelect.value;
        if (selectedValue.length == 0) {  // Empty selection or empty list
            return;
        }

        const delete_url = "/delete/" + selectedValue;  // XXX use Jinja2: {{ url_for("delete") | tojson }}
        // const delete_arg = {"method": "GET"};
        fetch(delete_url)
            .then(response => response.json())
            .then(data => {
                const error = data['error'];
                if (error) {
                    alert(error);
                }
                else {
                    removeOptionFromMyScriptsSelect(selectedValue);
                }
                handleEmptySelection();
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
        const newScriptContents = "# Learning simulator script\n# Created " + fullDateStr;
        const dataSend = {'name': newScriptName, 'code': newScriptContents};

        const add_url = "/add";  // XXX use Jinja2: {{ url_for("add") | tojson }}
        const add_arg = {"method": "POST",
                         "headers": {"Content-Type": "application/json"},
                         "body": JSON.stringify(dataSend)};

        fetch(add_url, add_arg)
            .then(response => response.json())
            .then(data => {
                const newScriptValue = data['id'];
                addOptionToMyScriptsSelect(newScriptName, newScriptValue);
            });

    }


}
