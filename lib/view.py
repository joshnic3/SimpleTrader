from flask import render_template
from datetime import datetime


def pp_key(key):
    return ' '.join([w.capitalize() for w in key.split('_')])


def pp_value(value, datatime_format='%H:%M', replace_none=None):
    if isinstance(value, datetime):
        return value.strftime(datatime_format)
    elif isinstance(value, float):
        return round(value, 5)
    elif replace_none is not None and value is None:
        return replace_none
    else:
        return value


def flatten(list_of_dicts):
    dict_in = {}
    out = []
    for d in list_of_dicts:
        dict_in.update(d)
        run = {}
        for key, value in dict_in.items():
            if isinstance(value, dict):
                for inner_key, inner_value in value.items():
                    run[key + '_' + inner_key] = inner_value
            else:
                run[key] = value
        out.append(run)
    return out


def shorten(text):
    words = text.split('_')
    letters = [w[0].upper() for w in words]
    return ''.join(letters)


def to_cols(rows, shorten_keys=False):
    table = {}
    for row in rows:
        for key, value in row.items():
            key = shorten(key) if shorten_keys else key
            if key in table:
                table[key].append(value)
            else:
                table[key] = [value]
    return table


def html_table(rows, headers, datatime_format=None, replace_none=None):
    flattened_run_log = flatten(rows)
    columns = to_cols(flattened_run_log)
    if columns:
        for column in columns:
            columns[column] = [pp_value(v, datatime_format, replace_none) for v in columns.get(column)]
        length = len(columns.get(headers[0]))
        filters = {col: sorted(list(set(columns.get(col))), reverse=(col == 'time')) for col in columns if not col == '-'}
        return render_template('table.html', headers=headers, columns=columns, length=length, filters=filters)
    return None


class View:

    DEFAULT_INTERVAL = 5

    @staticmethod
    def json_model(static_model):
        model_dict = static_model.as_dict()
        model_dict['series']['times'] = [pp_value(v) for v in model_dict.get('series').get('times')]
        model_dict['params'] = {k: pp_value(v) for k, v in model_dict.get('params').items()}
        model_dict['values'] = {k: pp_value(v) for k, v in model_dict.get('values').items()}
        return model_dict

    @staticmethod
    def runs_html(controller):
        if controller.runs:
            headers = ['time', 'run_type', 'order', 'error']
            for run in controller.runs:
                run['order'] = str(run.get('order'))
            return html_table(controller.runs, headers, datatime_format='%H:%M:%S', replace_none='-')
        return '<p>No Runs</p>'

    @staticmethod
    def orders_html(controller):
        controller.trader.update_orders()
        orders = controller.trader.orders
        if orders:
            headers = ['time', 'id', 'symbol', 'status', 'side', 'units', 'price']
            return html_table(orders, headers, datatime_format='%H:%M:%S', replace_none='-')
        return '<p>No Orders</p>'

    @staticmethod
    def view(static_model, refresh_interval=None):
        refresh_interval = int(refresh_interval) if refresh_interval is not None else View.DEFAULT_INTERVAL
        static = 'true' if refresh_interval < 1 else 'false'
        model = View().json_model(static_model)
        return render_template('view.html', model=model, static=static, refresh_interval=refresh_interval)
