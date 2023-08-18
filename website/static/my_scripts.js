document.addEventListener("DOMContentLoaded", onLoad);

function onLoad() { // DOM is loaded and ready

    makeFlashesFade();

    const usersScripts = document.getElementById('select-userscripts');
    const createButton = document.getElementById('button-createscript');
    const deleteButton = document.getElementById('button-deletescript');
    const openButton = document.getElementById('button-openscript');
    const previewCode = document.getElementById('textarea-code-preview');
    const previewText = document.getElementById('text-code-preview');

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
    if (openButton) {  // This button is only displayed when logged in
        openButton.addEventListener('click', openScriptButtonClicked);
    }

    handleVisibility();

    /* Get the values in the current selection in the users scripts list. */
    function getSelectedUserScripts() {
        return Array.from(usersScripts.querySelectorAll("option:checked"), e => e.value);
    }

    /* Get the names in the current selection in the users scripts list. */
    function getSelectedUserScriptNames() {
        return Array.from(usersScripts.querySelectorAll("option:checked"), e => e.text);
    }

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

    /* Listener. */
    function userScriptsSelectionChanged() {
        const selectedValues = getSelectedUserScripts();

        if (selectedValues.length != 1) {  // Multiple or empty selection or empty list
            handleVisibility();
            return;
        }
        const selectedValue = selectedValues[0];

        // Use cache if possible - otherwise fetch from database on server
        if (Object.hasOwn(cachedScripts, selectedValue)) {
            const code = cachedScripts[selectedValue].getCode();
            previewCode.value = code;
            handleVisibility();
        }
        else {
            const get_url = "/get/" + selectedValue;  // XXX use Jinja2: {{ url_for("get") | tojson }}
            fetch(get_url)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(networkErrorMsg(response, "Error reading script."));
                    }
                    return response.json();
                })
                .then(data => {
                    const err = data['error'];
                    if (err) {
                        throw new Error(err);
                    }
                    else {
                        const name = data['name'];
                        const code = data['code'];
                        previewCode.value = code;
                        updateCachedScripts(selectedValue, name, code);
                        handleVisibility();
                    }
                })
                .catch (error => {
                    alert(makeErrorMsg(error));
                });
        }
    }


    /* Handle visibility of elements based on selection in list of scripts. */
    function handleVisibility() {
        const selectedScriptNames = getSelectedUserScriptNames();
        const nSelectedValues = selectedScriptNames.length;
        const showScript = (nSelectedValues == 1);
        if (!showScript) {
            previewCode.value = "";
            previewText.innerHTML = "Preview";
        }
        else {
            previewText.innerHTML = "Preview of script " + selectedScriptNames[0];
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
        if (openButton) {
            const showOpenButton = (nSelectedValues === 1);
            if (showOpenButton) {
                openButton.style.display = "";
            }
            else {
                openButton.style.display = "none";
            }
        }
    }

    // function handleVisibility() {
    //     const nSelectedValues = getSelectedUserScripts().length;
    //     if (deleteButton) {  // This button is only displayed when logged in
    //         const showDeleteButton = (nSelectedValues >= 1);
    //         if (showDeleteButton) {
    //             deleteButton.style.display = "";
    //         }
    //         else {
    //             deleteButton.style.display = "none";
    //         }
    //     }
    // }

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

    /* Listener. */
    function deleteScriptButtonClicked() {
        const selectedValues = getSelectedUserScripts();
        if (selectedValues.length == 0) {  // Empty selection or empty list
            return;
        }

        if (!confirm("Are you sure you want to delete the selected scripts?")) {
            return;
        }

        const dataSend = {'ids': selectedValues};
        const delete_url = "/delete";  // XXX use Jinja2: {{ url_for("delete") | tojson }}
        const delete_arg = {"method": "POST",
                            "headers": {"Content-Type": "application/json"},
                            "body": JSON.stringify(dataSend)};
        fetch(delete_url, delete_arg)
            .then(response => {
                if (!response.ok) {
                    throw new Error(networkErrorMsg(response, "Error deleting script."));
                }
                return response.json();
            })
            .then(data => {
                const err = data['error'];
                const name = data['name'];
                if (err) {
                    throw new Error(err);
                }
                else {
                    for (let selectedValue of selectedValues) {
                        removeOptionFromUsersScripts(selectedValue);
                    }
                    displayFlashMessage("Deleted script " + name);
                }
                handleVisibility();
            })
            .catch (error => {
                alert(makeErrorMsg(error));
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
            .then(response => {
                if (!response.ok) {
                    throw new Error(networkErrorMsg(response, "Error creating new script."));
                }
                return response.json();
            })
            .then(data => {
                const err = data['error'];
                if (err) {
                    throw new Error(err);
                }
                else {
                    const newScriptValue = data['id'];
                    addOptionToUsersScripts(newScriptName, newScriptValue);
                    displayFlashMessage("Created script " + newScriptName);
                }
            })
            .catch (error => {
                alert(makeErrorMsg(error));
            });
    }

    /* Listener. */
    function openScriptButtonClicked() {
        const selectedValues = getSelectedUserScripts();
        if (selectedValues.length !== 1) {  // Should never happen since the Open button is only visible when single selection
            return;
        }
        const selectedValue = selectedValues[0];

        const get_url = "/simulate/" + selectedValue;  // XXX use Jinja2: {{ url_for("get") | tojson }}
        fetch(get_url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(networkErrorMsg(response, "Error opening script."));
                }
                window.location.pathname = ('/simulate/' + selectedValue);
            })
            .catch (error => {
                alert(makeErrorMsg(error));
            });


        // // const dataSend = {'id': selectedValue};
        // const open_url = "/open/" + selectedValue;  // XXX use Jinja2: {{ url_for("delete") | tojson }}
        // const open_arg = {"method": "GET"};
        //                 //   "headers": {"Content-Type": "application/json"}};
        //                 //   "body": JSON.stringify(dataSend)};
        // fetch(open_url, open_arg)
        //     .then(response => response.json())
        //     .then(data => {
        //         const error = data['error'];
        //         if (error) {
        //             alert(error);
        //         }
        //         else {
        //             for (let selectedValue of selectedValues) {
        //                 removeOptionFromUsersScripts(selectedValue);
        //             }
        //         }
        //         handleVisibility();
        //     }
        // );


    }
    

}
