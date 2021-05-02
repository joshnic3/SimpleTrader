
function requestHtml(endpoint, elementId){
    const request = new Request('http://127.0.0.1:5000' + endpoint);
    fetch(request).then(function (response) {
        return response.text();
    }).then(function (html) {
        document.getElementById(elementId).innerHTML = html;
    }).catch(function (err) {
        warn('Bad View Request: ' + err);
        console.warn('Something went wrong.', err);
    });
}

function postRequest(endpoint, callback) {
    const request = new Request('http://127.0.0.1:5000' + endpoint);
    fetch(request).then(function (response) {
        return response.json();
    }).then(function (data) {
        callback(data);
    }).catch(function (err) {
        warn('Bad Post Request: ' + err);
        console.warn('Something went wrong.', err);
    });
}


function editParamModal(key, value) {
    document.getElementById("editModal").classList.add('show');
    document.getElementById("newValueInput").value = value;
    document.getElementById("paramKey").innerHTML = key;
}

function closeEditParamModel() {
    editModal = document.getElementById("editModal");
    editModal.classList.remove('show');
}

function modify() {
    key = document.getElementById("paramKey").innerHTML;
    value = document.getElementById("newValueInput").value;
    closeEditParamModel();
    console.log('Modifying ' + key + ': ' + value);
    endpoint = "/controller/modify?k=" + key + "&v=" + value;
    console.log(endpoint);
    postRequest(endpoint, modifyCallback);
}

function modifyCallback(data) {
    if ('error' in data) {
        warn(data.error);
    } else {
        success('<strong>Modified Parameter</strong>: ' + data.modified.key + ': ' + data.modified.value);
    }
}

function running(data) {
    if (data.isRunning) {
        runButton = document.getElementById("runButton");
        stopButton = document.getElementById("stopButton");
        runOnceButton = document.getElementById("runOnceButton");

        runButton.classList.add("disabled");
        runButton.classList.remove("btn-warning");
        runButton.classList.add("btn-outline-success");
        runButton.innerHTML = 'Running... <div id="runningSpinner" class="spinner-border spinner-border-sm text-success" role="status" data-bs-toggle="tooltip" data-bs-placement="right" title="Running"></div>';
        runButton.blur();

        stopButton.classList.remove("disabled");
        stopButton.classList.remove("btn-outline-danger");
        stopButton.classList.add("btn-danger");

        runOnceButton.classList.add("disabled");
    } else {
        warn('Failed to start process');
    }
}

function run() {
    runButton = document.getElementById("runButton");
    runButton.classList.add("disabled");
    runButton.classList.add("btn-warning");
    runButton.classList.remove("btn-success");
    runButton.innerHTML = 'Starting...';
    runButton.blur();

    postRequest('/controller/start', runCallback)
}

function runCallback(data) {
    if (data.started) {
        console.log('Started');
    } else {
        warn('Failed to start.');
    }
}

function stopped(data) {
    if (!data.isRunning) {
        runButton = document.getElementById("runButton");
        stopButton = document.getElementById("stopButton");
        runOnceButton = document.getElementById("runOnceButton");

        runButton.classList.remove("disabled");
        runButton.classList.remove("btn-warning");
        runButton.classList.add("btn-success");
        runButton.innerHTML = 'Auto';

        stopButton.classList.add("disabled");
        stopButton.classList.remove("btn-danger");
        stopButton.classList.add("btn-outline-danger");
        stopButton.blur();

        runOnceButton.classList.remove("disabled");
    } else {
        warn('Failed to stop process');
    }
}

function stop() {
    runButton = document.getElementById("runButton");
    runButton.classList.remove("btn-outline-success");
    runButton.classList.add("btn-warning");
    runButton.innerHTML = 'Stopping..';

    postRequest('/controller/stop', stopCallback);
}

function stopCallback(data) {
    if (data.stopped) {
        console.log('Stopped');
    } else {
        warn('Failed to stop.');
    }
}

function ranOnceCallback(data) {
    if (data.ran) {
        console.log('Ran Once');
    } else {
        warn('Failed to set off run.');
    }
}

function runOnce() {
   runButton.classList.add("disabled");
    runButton.classList.add("btn-warning");
    runButton.classList.remove("btn-success");
    runButton.innerHTML = 'Running once...';
    runButton.blur();
    postRequest('/controller/once', ranOnceCallback);
}

function warn(message) {
    warningAlert = document.getElementById("warningAlert");
    if (warningAlert != null) {
        warningAlert.classList.remove("collapse");
        document.getElementById("warningAlertMessage").innerHTML = '<strong>Warning!</strong> ' + message;
    }
}

function success(message) {
    successAlert = document.getElementById("successAlert");
    if (successAlert != null) {
        successAlert.classList.remove("collapse");
        document.getElementById("successAlertMessage").innerHTML = message;
    }
}

function dismissWarm() {
    warningAlert = document.getElementById("warningAlert");
    warningAlert.classList.add("collapse");
}

function dismissSuccess() {
    successAlert = document.getElementById("successAlert");
    successAlert.classList.add("collapse");
}

function refreshRunView() {
    runReportFrame = document.getElementById('runReport')
    runReportFrame.contentWindow.location.reload();
}

function updateController() {
    const request = new Request('http://127.0.0.1:5000/controller/update');
    fetch(request).then(function (response) {
        return response.json();
    }).then(function (data) {
//        console.log(data.status)
        orderCountDiv = document.getElementById("ordersLink");
        runCountDiv = document.getElementById("runsLink");
        if (data.status.isRunning) {
            running(data.status);
        } else {
            stopped(data.status);
        }
        if (data.status.orderCount != orderCountDiv.title) {
            orderCountDiv.title = data.status.orderCount;
        }
        if (data.status.runCount != runCountDiv.title) {
            runCountDiv.title = data.status.runCount;
        }

        if (data.status.orderCount > 0) {
            orderCountDiv.classList.remove('disabled');
        }

        if (data.status.runCount > 0) {
            runCountDiv.classList.remove('disabled');
        }
        }).catch(function (err) {
            alert("Lost connection to controller! Ensure server is running and then press OK");
            dismissWarm();
        });
        live();
}

function clearActiveTabs() {
    document.getElementById('runsLink').classList.remove('active');
    document.getElementById('ordersLink').classList.remove('active');
}

function showControllerTab(view) {
    frame = document.getElementById('controllerFrame');
    collapseControllerView = document.getElementById('collapseControllerView');

    link = document.getElementById(view+'Link');
    runsLink = document.getElementById('runsLink');
    ordersLink = document.getElementById('ordersLink');
    frame.src = "http://127.0.0.1:5000/view/" + view;

    clearActiveTabs();
    link.classList.add('active');
    collapseControllerView.classList.add('show');

}

function static() {
    heartbeat = document.getElementById("heartbeat");
    heartbeat.classList.add("bg-warning");
    heartbeat.classList.add("text-dark");
    heartbeat.innerHTML = "STATIC";
    document.getElementById("runButton").disabled = true;
    document.getElementById("runOptions").disabled = true;
}

function live() {
    heartbeat = document.getElementById("heartbeat");
    heartbeat.classList.add("bg-primary");
    heartbeat.classList.remove("bg-warning");
    heartbeat.classList.remove("text-dark");
    heartbeat.innerHTML = new Date().toLocaleTimeString();
    document.getElementById("runButton").disabled = false;
    document.getElementById("runOptions").disabled = false;
}