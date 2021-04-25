const CHART_INITIAL_CONFIG = {
  labels: [],
  datasets: [
      {
        label: 'SYMBOL',
        data: [],
        borderColor: 'rgb(255, 204, 0)',
        borderWidth: 3,
        fill: false,
        tension: 0.1,
        pointBorderColor: 'rgb(51, 51, 204)',
        pointBackgroundColor: 'rgba(51, 51, 204 ,0.5)',
        pointRadius: 0.2,
        pointHoverRadius: 10,
        pointStyle: 'circle'
      },
      {
        label: 'Buy Limit',
        data: [],
        borderColor: 'rgb(51, 204, 51)',
        borderWidth: 1.5,
        fill: false,
        pointRadius: 0,
        borderDash: [9,3]
      },
      {
        label: 'Sell Limit',
        data: [],
        borderColor: 'rgb(255, 80, 80)',
        borderWidth: 1.5,
        fill: false,
        pointRadius: 0,
        borderDash: [9,3]
      },

  ]
};
const CHART_OPTIONS = {
    plugins: {
        legend: {
            display: true,
            labels : {boxWidth: 1}
        }
    },
    animation: {
        duration: 0
    }
};

function updateGraph(model, graph) {
    graph.data.labels = [];
    graph.data.datasets[0].data = [];
    graph.data.datasets[1].data = [];
    graph.data.datasets[2].data = [];
    for (i = 0; i < model.series.times.length; i++) {
        graph.data.labels.push(model.series.times[i]);
        graph.data.datasets[0].data.push(model.series.values[i]);
        graph.data.datasets[1].data.push(model.series.buy_limits[i]);
        graph.data.datasets[2].data.push(model.series.sell_limits[i]);
    }
    graph.data.datasets[0].label = model.params.ticker;
    graph.update();
}

function updateList(model, list_key) {
    for (key in model[list_key]) {
        document.getElementById(key).innerHTML = model[list_key][key];
    }
}

function updateModel(graph) {
    const request = new Request('http://127.0.0.1:5000/controller/update');
    fetch(request).then(function (response) {
        response = response.json();
        return response;
    }).then(function (response) {
        model = response.model;
        updateGraph(model, graph);
        updateList(model, 'params');
        updateList(model, 'values');
    }).catch(function (err) {
        warn('Bad View Request: ' + err);
        console.warn('Something went wrong.', err);
    });
}
