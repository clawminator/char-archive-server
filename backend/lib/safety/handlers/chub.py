from lib.safety.handlers.safety_handler import SafetyHandler


class ChubSafetyHandler(SafetyHandler):
    def __init__(self, **kwargs):
        super().__init__(def_table='chub_character_def',
                         meta_table='chub_character',
                         def_select_cols=('id', 'author', 'full_path', 'definition', 'metadata', 'added'),
                         def_primary_key='id',
                         meta_primary_key='id',
                         name_format='{full_path}',
                         tqdm_desc='Chub',
                         **kwargs)
