const CHART_INITIAL_CONFIG = {
  labels: [],
  datasets: [
      {
        label: 'ticks',
        data: [],
        borderColor: 'rgb(255, 204, 0)',
        borderWidth: 2.0,
        fill: false,
        tension: 0.1,
        pointBorderColor: 'rgb(51, 51, 204)',
        pointBackgroundColor: 'rgba(51, 51, 204 ,0.5)',
        pointRadius: 0.2,
        pointHoverRadius: 10,
        pointStyle: 'circle'
      },
      {
        label: 'buy_limits',
        data: [],
        borderColor: 'rgb(51, 204, 51)',
        borderWidth: 1.0,
        fill: {
            target: 'origin',
            above: 'rgba(51, 204, 51, 0.1)'    // Area will be red above the origin // And blue below the origin
        },
        pointRadius: 0,
        borderDash: [9,3]
      },
      {
        label: 'sell_limits',
        data: [],
        borderColor: 'rgb(255, 80, 80)',
        borderWidth: 1.0,
        fill: {
            target: 'end',
            below: 'rgba(255, 80, 80, 0.1)'    // Area will be red above the origin // And blue below the origin
        },
        pointRadius: 0,
        borderDash: [9,3]
      },
      {
        label: 'rolling_mean',
        data: [],
        borderColor: 'rgb(255, 0, 255)',
        borderWidth: 1.0,
        fill: false,
        pointRadius: 0,
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
    graph.data.datasets[0].label = 'ticks';
    for (i = 0; i < model.series.times.length; i++) {
        graph.data.labels.push(model.series.times[i]);
        for (j in graph.data.datasets) {
            key = graph.data.datasets[j].label;
            graph.data.datasets[j].data.push(model.series[key][i]);
        }
    }
    graph.data.datasets[0].label = model.params.ticker;
    graph.update();
}

function updateTable(model, list_key) {
    for (key in model[list_key]) {
        document.getElementById(key).innerHTML = model[list_key][key];
    }
}
