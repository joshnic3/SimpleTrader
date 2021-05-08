import os
import webbrowser

from flask import Flask, jsonify

from lib.utilities.setup import configure_controller, read_configs_from_yaml_file, read_cmdline_args, setup_logger
from lib.utilities.web import get_params_from_request, local_only
from lib.view import View

web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'web')
app = Flask(
    __name__,
    static_url_path='',
    static_folder=os.path.join(web_dir, 'static'),
    template_folder=os.path.join(web_dir, 'templates')
)


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
            'orderCount': len(controller.trader.trades),
            'errorCount': len(controller.errors),
            'exchangeApi': controller.trader.exchange.base,
            'sessionPnl': controller.trader.pnl
        }
    }
    return jsonify(data)


@app.route("/view/runs", methods=['GET'])
@local_only
def get_runs():
    limit = get_params_from_request('limit', cast=int)
    return View.runs_html(controller, limit=limit)


@app.route("/view/trades", methods=['GET'])
@local_only
def get_orders():
    limit = get_params_from_request('limit', cast=int)
    controller.trader.update()
    return View.trades_html(controller, limit=limit)


@app.route("/", methods=['GET'])
@local_only
def view():
    controller.update_model()
    static_model = controller.return_static_model()
    refresh_rate = get_params_from_request('r', cast=int)
    return View.view(static_model, refresh_rate)


if __name__ == '__main__':
    args = read_cmdline_args()
    configs = read_configs_from_yaml_file(args.configs)

    setup_logger('server', configs.get('logs'))
    controller = configure_controller(configs, args.account, test=args.test_exchange)

    if args.browser:
        webbrowser.open('http://127.0.0.1:5000')

    app.run(host='127.0.0.1', debug=args.debug)


