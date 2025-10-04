from lib.safety.handlers.safety_handler import SafetyHandler


class CharTavernSafetyHandler(SafetyHandler):
    def __init__(self, **kwargs):
        super().__init__(def_table='char_tavern_character_def',
                         meta_table='char_tavern_character',
                         def_select_cols=('path', 'definition', 'metadata', 'added'),
                         def_primary_key='path',
                         meta_primary_key='path',
                         name_format='{path}',
                         tqdm_desc='Character Tavern',
                         **kwargs)
