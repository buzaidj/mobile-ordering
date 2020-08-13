from escpos.printer import Usb, Dummy
p = Dummy()

def print_line(name, text):
    p.textln(name + ": " + str(text))
    print(name + ": " + str(text))

def print_blank():
    p.textln("")
    print()
