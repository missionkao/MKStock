import re
import locale

class Utility:

    @classmethod
    def str_to_float(cls, string):
        try:
            num = re.search(r"[-+]?\d*\.\d+|\d+", string).group()
            return float(num)
        except AttributeError:
            return 0

    @classmethod
    def volume_to_float(cls, volume):
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        return locale.atof(volume)
