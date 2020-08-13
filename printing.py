from escpos.printer import Usb, Dummy
p = Dummy()

def print_line(name, text):
    p.text(name + ": " + str(text) + "\n")
    print(name + ": " + str(text))

def print_text_line(text):
    p.text(text + "\n")
    print(text)

def print_blank():
    p.text("\n")
    print()
