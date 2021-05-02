import os

from flask import Flask, request, jsonify

import webbrowser

from lib.utilities.setup import setup_controller, read_configs_from_yaml_file
from lib.utilities.web import get_params_from_request, local_only
from lib.view import View



yaml_file_path = '/Users/joshnicholls/Desktop/SimpleTrader/configs.yaml'
open_browser = False


configs = read_configs_from_yaml_file(yaml_file_path)
controller = setup_controller(configs, 'BinanceSimpleTrader', test=False)

web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'web')
app = Flask(
    __name__,
    static_url_path='',
    static_folder=os.path.join(web_dir, 'static'),
    template_folder=os.path.join(web_dir, 'templates')
)


if open_browser:
    webbrowser.open('http://127.0.0.1:5000')


@app.route("/controller/start")
@local_only
def start():
    controller.run()
    return jsonify({'started': controller.running})


@app.route("/controller/once")
@local_only
def once():
    runs_before = len(controller.runs)
    controller.run_once()
    runs_after = len(controller.runs)
    return jsonify({'ran': runs_after > runs_before})


@app.route("/controller/stop")
@local_only
def stop():
    controller.stop()
    return jsonify({'stopped': not controller.running})


@app.route("/controller/modify")
@local_only
def modify_parameter():
    key = get_params_from_request('k')
    if controller.model.params.get(key) is None:
        return jsonify({'error': 'Invalid key: {}'.format(key)})
    value = get_params_from_request('v')
    result = controller.modify_parameter(key, value)
    return jsonify({'modified': {'key': key, 'value': result}})


@app.route("/controller/update")
@local_only
def update():
    controller.update_model()
    static_model = controller.return_static_model()
    data = {
        'model': View.json_model(static_model),
        'status': {
            'isRunning': controller.running,
            'runCount': len(controller.runs),
            'orderCount': len(controller.trader.orders),
            'errorCount': len(controller.errors),
            'exchangeApi': controller.trader.exchange.base
        }
    }
    return jsonify(data)


@app.route("/view/runs")
@local_only
def get_runs():
    return View.runs_html(controller)


@app.route("/view/orders")
@local_only
def get_orders():
    controller.trader.update_orders()
    return View.orders_html(controller)


@app.route("/", methods=['GET'])
@local_only
def view():
    controller.update_model()
    static_model = controller.return_static_model()
    refresh_rate = get_params_from_request('r', cast=int)
    return View.view(static_model, refresh_rate)


if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)

