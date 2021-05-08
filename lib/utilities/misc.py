def dict_to_string(input_dict):
    return ', '.join(['{}: {}'.format(k, v) for k, v in input_dict.items()])
