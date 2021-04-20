import ctypes,sys

class ColorPrint(object):
    TEXT_COLORS = {
            'black': 0x00, 'dark_blue': 0x01, 'dark_green': 0x02, 'dark_skyblue': 0x03, 
            'dark_red': 0x04, 'dark pink': 0x05, 'dark yellow': 0x06, 'dark white': 0x07, 
            'dark gray': 0x08, 'blue': 0x09, 'green': 0x0a, 'skyblue': 0x0b, 
            'red': 0x0c, 'pink': 0x0d, 'yellow': 0x0e, 'white': 0x0f
        }
    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    STD_ERROR_HANDLE = -12
    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    
    @staticmethod
    def cprint(string: str, c: str, end='\n'):
        Bool = ctypes.windll.kernel32.SetConsoleTextAttribute(
            ColorPrint.std_out_handle, ColorPrint.TEXT_COLORS[c])
        sys.stdout.write(u'{}'.format(string+end))
        Bool = ctypes.windll.kernel32.SetConsoleTextAttribute(
            ColorPrint.std_out_handle, 0x0c | 0x0a | 0x09)


if __name__ == '__main__':
    ColorPrint.cprint("Hello world", 'blue')