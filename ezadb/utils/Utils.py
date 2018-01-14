import os
from pygubu.stockimage import StockImage, StockImageException

# Initialize images
APP_DIR = path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
IMAGES_DIR = os.path.join(APP_DIR, "images")
StockImage.register_from_dir(IMAGES_DIR)


class Utils:
    @staticmethod
    def replace_all(text, dic):
        """"Returns a string replacing all the sequence of characters defined in the dictionary . """
        for key, value in dic.items():
            text = text.replace(key, value)
        return text

    @staticmethod
    def set_app_icon(tk_top_level):
        try:
            tk_top_level.wm_iconname('ezadb')
            tk_top_level.tk.call('wm', 'iconphoto', tk_top_level._w, StockImage.get('ezadb'))
        except StockImageException as e:
            pass
