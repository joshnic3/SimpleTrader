function editParamModal(key, value) {
    document.getElementById("editModal").classList.add('show');
    document.getElementById("newValueInput").value = value;
    document.getElementById("paramKey").innerHTML = key;
}

function closeEditParamModel() {
    editModal = document.getElementById("editModal");
    editModal.classList.remove('show');
}

function running(isRunning) {
    if (isRunning) {
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

function stopped(isRunning) {
    if (!isRunning) {
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

function warn(message) {
    warningAlert = document.getElementById("warningAlert");
    if (warningAlert != null) {
        warningAlert.classList.remove("collapse");
        document.getElementById("warningAlertMessage").innerHTML = '<strong>Warning!</strong> ' + message;
    }
}

function dismissWarm() {
    warningAlert = document.getElementById("warningAlert");
    warningAlert.classList.add("collapse");
}

function success(message) {
    successAlert = document.getElementById("successAlert");
    if (successAlert != null) {
        successAlert.classList.remove("collapse");
        document.getElementById("successAlertMessage").innerHTML = message;
    }
}

function dismissSuccess() {
    successAlert = document.getElementById("successAlert");
    successAlert.classList.add("collapse");
}

function showControllerTab(view) {
    frame = document.getElementById('controllerFrame');
    collapseControllerView = document.getElementById('collapseControllerView');
    tradeCount = document.getElementById('tradeCount');

    link = document.getElementById(view+'Link');
    runsLink = document.getElementById('runsLink');
    tradesLink = document.getElementById('tradesLink');
    frame.src = "http://127.0.0.1:5000/view/" + view;

    clearActiveTabs();
    link.classList.add('active');
    collapseControllerView.classList.add('show');

    if (view == 'trades') {
        tradeCount.classList.remove('bg-warning');
        tradeCount.classList.add('bg-secondary');
    }
}

function clearActiveTabs() {
    document.getElementById('runsLink').classList.remove('active');
    document.getElementById('tradesLink').classList.remove('active');
}

function refreshRunView() {
    runReportFrame = document.getElementById('runReport')
    runReportFrame.contentWindow.location.reload();
}