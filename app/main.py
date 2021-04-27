import os

from flask import Flask, request, jsonify

from lib.utilities.setup import setup_controller, read_configs_from_yaml_file
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
def start():
    controller.run()
    return jsonify({'isRunning': controller.running})


@app.route("/controller/once")
def once():
    controller.run_once()
    return jsonify({'isRunning': controller.running})


@app.route("/controller/stop")
def stop():
    controller.stop()
    return jsonify({'isRunning': controller.running})


@app.route("/controller/update")
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
def get_runs():
    return View.runs_html(controller)


@app.route("/view/orders")
def get_orders():
    controller.trader.update_orders()
    return View.orders_html(controller)


@app.route("/", methods=['GET'])
def view():
    controller.update_model()
    static_model = controller.return_static_model()
    try:
        refresh_rate = int(request.args.get('r'))
    except TypeError:
        refresh_rate = None
    except ValueError:
        refresh_rate = None
    return View.view(static_model, refresh_rate)


if __name__ == '__main__':
    app.run(debug=True)

