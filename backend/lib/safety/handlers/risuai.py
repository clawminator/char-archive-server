from lib.safety.handlers.safety_handler import SafetyHandler


class RisuaiSafetyHandler(SafetyHandler):
    def __init__(self, **kwargs):
        super().__init__(def_table='risuai_character_def',
                         meta_table='risuai_character',
                         def_select_cols=('id', 'author', 'name', 'definition', 'metadata'),
                         def_primary_key='id',
                         meta_primary_key='id',
                         name_format='{author}/{name} {id}',
                         tqdm_desc='Risuai',
                         **kwargs)
