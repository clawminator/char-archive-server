from urllib.parse import unquote


def parse_int_arg(item: str, item_name: str, allow_negative_one: bool = False):
    try:
        item = int(item)
    except:
        return None, f'invalid {item_name}'
    if not allow_negative_one and item < 0:
        return None, f'invalid {item_name}'
    elif allow_negative_one and item < -1:
        return None, f'invalid {item_name}'
    return item, None


def double_decode_url_param(string: str):
    return unquote(unquote(string, encoding='utf-8', errors='replace'), encoding='utf-8', errors='replace')
