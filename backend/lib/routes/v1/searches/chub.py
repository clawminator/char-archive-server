from lib.search.handlers.chub import ChubSearchNode


def parse_chub_item(args: dict):
    chub_key_fields = {}
    for key, _ in ChubSearchNode.model_fields.items():
        if args.get(key):
            v = args[key]
            if key == 'chub_fullPath':
                v = v.split('/')
            chub_key_fields['chub.' + key] = v
    return chub_key_fields
