from lib.safety.handlers.safety_handler import SafetyHandler


class WebringSafetyHandler(SafetyHandler):
    def __init__(self, **kwargs):
        super().__init__(def_table='webring_character_def',
                         meta_table='webring_character_def',
                         def_select_cols=('card_data_hash', 'author', 'name', 'definition', 'metadata'),
                         def_primary_key='card_data_hash',
                         meta_primary_key='card_data_hash',
                         name_format='{author}/{name} {card_data_hash}',
                         tqdm_desc='Webring',
                         **kwargs)
