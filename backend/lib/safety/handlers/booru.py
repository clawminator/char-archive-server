from lib.safety.handlers.safety_handler import SafetyHandler


class BooruSafetyHandler(SafetyHandler):
    def __init__(self, **kwargs):
        super().__init__(def_table='booru_character_def',
                         meta_table='booru_character_def',
                         def_select_cols=('id', 'author', 'name', 'definition', 'metadata'),
                         def_primary_key='id',
                         meta_primary_key='id',
                         name_format='{author}/{name} {id}',
                         tqdm_desc='Booru',
                         **kwargs)
