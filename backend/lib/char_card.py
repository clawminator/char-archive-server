import base64
import json

from PIL.PngImagePlugin import PngInfo


def generate_png_chara(data: dict):
    """
    https://github.com/FaceDeer/pyqt_tavernai_character_editor/blob/main/tavernAI%20character%20editor.py
    """
    json_str = json.dumps(data)
    base64_str = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    metadata = PngInfo()
    metadata.add_text('chara', base64_str)
    return metadata
