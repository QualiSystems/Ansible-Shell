

def _get_comma_separated_params(key_value_pair_str):
    """
    parse, clean, and add to request object
    :param str key_value_pair_str: expected 'input1, val1'
    :return:
    """
    split = key_value_pair_str.split(",")
    cleaned = [s.strip() for s in split]
    if len(cleaned) > 2:
        raise Exception("Parsed Key-pair is greater than 2")
    return {"name": cleaned[0], "value": cleaned[1]}


def get_params_list_from_semicolon_sep_str(input_str):
    """
    "input1, val1; input2, val2; input 3, val3" --> [{"name": "input1", "value": "val1"}, ...]
    :param input_str: "input1, val1; input2, val2; input 3, val3"
    :return:
    """
    if not input_str:
        return []
    split = input_str.split(";")
    params_list = [_get_comma_separated_params(item) for item in split]
    return params_list


if __name__ == "__main__":
    # simple test
    input_str = "ansible_python_interpreter,/usr/bin/python3;input2, val2"
    my_params_list = get_params_list_from_semicolon_sep_str(input_str)
    print(my_params_list)
    pass
