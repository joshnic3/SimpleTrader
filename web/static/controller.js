
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
    runButton.innerHTML = 'Executing...';
    runButton.blur();
    postRequest('/controller/once', ranOnceCallback);
}

function updateController(status) {
    orderCountDiv = document.getElementById("tradesLink");
    runCountDiv = document.getElementById("runsLink");
    tradeCount = document.getElementById("tradeCount");
    if (status.isRunning) {
        running(status.isRunning);
    } else {
        stopped(status.isRunning);
    }
    if (status.orderCount != orderCountDiv.title) {
        orderCountDiv.title = status.orderCount;
        tradeCount.innerHTML = status.orderCount;
        tradeCount.classList.add('bg-warning');
        tradeCount.classList.remove('bg-secondary');
    }
    if (status.runCount != runCountDiv.title) {
        runCountDiv.title = status.runCount;
    }

    if (status.orderCount > 0) {
        orderCountDiv.classList.remove('disabled');
    }

    if (status.runCount > 0) {
        runCountDiv.classList.remove('disabled');
    }
}

function update(graph) {
    const request = new Request('http://127.0.0.1:5000/controller/update');
    fetch(request).then(function (response) {
        return response.json();
    }).then(function (data) {
        updateController(data.status);
        updateGraph(data.model, graph);
        updateTable(data.model, 'params');
        updateTable(data.model, 'values');
        }).catch(function (err) {
            console.log(err);
            alert("Lost connection to controller! Ensure server is running and then press OK");
            dismissWarm();
        });
        live();
    }