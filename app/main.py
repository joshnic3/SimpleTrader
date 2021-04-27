import os

from flask import Flask, request, jsonify

from lib.utilities.setup import setup_controller, read_configs_from_yaml_file
from lib.utilities.web import get_params_from_request, local_only
from lib.view import View


web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'web')
app = Flask(
    __name__,
    static_url_path='',
    static_folder=os.path.join(web_dir, 'static'),
    template_folder=os.path.join(web_dir, 'templates')
)

yaml_file_path = '/Users/joshnicholls/Desktop/SimpleTrader/configs.yaml'
configs = read_configs_from_yaml_file(yaml_file_path)
controller = setup_controller(configs, 'BinanceSimpleTrader', test=False)


@app.route("/controller/start")
@local_only
def start():
    controller.run()
    return jsonify({'isRunning': controller.running})


@app.route("/controller/once")
@local_only
def once():
    controller.run_once()
    return jsonify({'isRunning': controller.running})


@app.route("/controller/stop")
@local_only
def stop():
    controller.stop()
    return jsonify({'isRunning': controller.running})


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
    app.run(host='0.0.0.0', debug=True)

