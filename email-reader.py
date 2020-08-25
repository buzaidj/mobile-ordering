from imapclient import IMAPClient
import imapclient.exceptions
import json, time
from datetime import datetime, date, timedelta, timezone
import queue
import email
from email import policy

import pytz
from tzlocal import get_localzone

import phonenumbers


from escpos.printer import Usb, Dummy

# TODO: CHANGE TO INPUT FXN
username = input('username')
password = input('password')


# TODO : Add support for printing at a certain time using the orders_to_print queue/printing 10 mins before we want it to


class Order:
    needed_params = ['Name', 'Number', 'Order', 'Notes']

    email_time_format = '%a, %d %b %Y %H:%M:%S %z'
    date_format = "%b %-d"
    time_format = "%-I:%M:%S %p"

    tz = None
    while tz == None:
        try:
            tz = get_localzone()

        except Exception as e:
            print(e)
            print("Trying to get time zone again in 15 seconds")
            time.sleep(15)


    """
    Class to represent an order with a printer tied to it

    :param msgid: msg identifier number
    :param raw_email: raw email in bytes
    """
    def __init__(self, msgid, raw_email):
        """
        Initializes an order from a raw email and msg id
        """
        email_message = email.message_from_bytes(raw_email[b'RFC822'], policy = policy.default)
        self.order_type = email_message.get('Subject')
        body = str(email_message.get_body('text/plain'))
        body = body[body.find('{'): body.find('}') + 1]

        self.order_number = msgid % 100
        self.can_print = 'full'

        try:
            self.order_dict = json.loads(body)
            try:
                for x in self.needed_params:
                    assert x in self.order_dict
            except Exception as e:
                print(e)
                self.can_print = 'limited'
                # SECONDARY PRINTING OF MISFORMATTED MESSAGE THAT CAN STILL BE READ

        except Exception as e:
            self.order_dict = {}
            self.can_print = 'message format error'

        dt_str = str(email_message.get('Date'))
        self.dt = datetime.strptime(dt_str, self.email_time_format).astimezone(self.tz)
        self.date = self.dt.strftime(self.date_format)
        self.time = self.dt.strftime(self.time_format)


    """
    Print order to thermal receipt printer with instantiated order class

    :param p: instantiated connected printer
    """
    def print_order(self, p):
        if self.can_print == 'full':
            print_ticket(p, self.order_dict, self.order_type, self.order_number, self.date, self.time)
        elif self.can_print == 'limited':
            print_ticket_limited(p, self.order_dict, self.order_type, self.order_number, self.date, self.time)
        else:
            print_error_message(p, 'message formatted incorrectly')



"""
Print an error message to thermal receipt printer

:param p: instantiated connected printer
:param msg: message (as a string)
"""
def print_error_message(p, msg):
    try:
        d = Dummy()

        d.set(align = "left", bold = True, underline = 2, double_height = False, double_width = False, invert = True, density = 4, font = 'a')
        d.textln('ERROR: ' + msg)
        d.cut()

        p._raw(d.output)

    except Exception as e:
        print(e)

"""
Print a ticket to thermal receipt printer

:param p: instantiated connected printer
:param order_dict: dictionary of the order
    MUST have keys for "name, type, order, notes"
"""
def print_ticket(p, order_dict, order_type, order_number, order_date, order_time):
    try:
        d = Dummy()
        d.line_spacing(120)

        name = order_dict.pop('Name')
        number = order_dict.pop('Number')

        formatted_number = phonenumbers.format_number(phonenumbers.parse(number, 'US'), phonenumbers.PhoneNumberFormat.NATIONAL)

        order = order_dict.pop('Order')
        notes = order_dict.pop('Notes')

        d.set(align = "center", bold = True, underline = 2, double_height = False, double_width = False, custom_size = True, smooth = True, width = 2, height = 2, invert = False, density = 8, font = 'a')
        d.block_text(str(order_number) + ' ' + name + '\n', font = 'a')
        d.ln(1)

        d.set(align = "center", bold = False, underline = 0, double_height = False, double_width = False, custom_size = True, smooth = True, width = 2, height = 2, invert = False, density = 8, font = 'a')
        d.block_text(order_type + '\n', columns = 20, font = 'a')
        d.ln(1)

        d.text(formatted_number + '\n')
        d.text(order_date + '\n')
        d.text(order_time + '\n')
        d.text(' \n')


        d.set(align = "left", bold = True, underline = 0, double_height = False, double_width = False, custom_size = True, smooth = True, width = 2, height = 2, invert = False, density = 8, font = 'b')
        d.text('ORDER\n')

        d.set(align = "left", bold = False, underline = 0, double_height = False, double_width = False, custom_size = True, smooth = True, width = 2, height = 2, invert = False, density = 8, font = 'a')
        d.block_text(order + '\n', columns = 20, font = 'a')

        d.ln(2)

        if notes != '':
            d.set(align = "left", bold = True, underline = 0, double_height = False, double_width = False, custom_size = True, smooth = True, width = 2, height = 2, invert = False, density = 8, font = 'b')
            d.text('NOTES\n')

            d.set(align = "left", bold = False, underline = 0, double_height = False, double_width = False, custom_size = True, smooth = True, width = 2, height = 2, invert = False, density = 8, font = 'a')
            d.block_text(notes + '\n', columns = 20, font = 'a')

        d.cut()

        p._raw(d.output)

    except Exception as e:
        print(e)

def print_ticket_limited(p, order_dict, order_type, order_number, order_date, order_time):
    try:
        d = Dummy()
        d.line_spacing(120)

        d.set(align = "center", bold = True, underline = 2, double_height = False, double_width = False, custom_size = True, smooth = True, width = 2, height = 2, invert = False, density = 8, font = 'a')
        d.block_text(str(order_number) + ' ' + '\n', font = 'a')
        d.ln(1)

        d.set(align = "center", bold = False, underline = 0, double_height = False, double_width = False, custom_size = True, smooth = True, width = 2, height = 2, invert = False, density = 8, font = 'a')
        d.block_text(order_type + '\n', columns = 20, font = 'a')
        d.ln(1)

        d.text(order_date + '\n')
        d.text(order_time + '\n')
        d.text(' \n')


        d.set(align = "left", bold = True, underline = 0, double_height = False, double_width = False, custom_size = True, smooth = True, width = 2, height = 2, invert = False, density = 8, font = 'b')
        d.text('ORDER DETAILS\n')

        d.set(align = "left", bold = False, underline = 0, double_height = False, double_width = False, custom_size = True, smooth = True, width = 2, height = 2, invert = False, density = 8, font = 'a')
        for k, v in order_dict.items():
            d.block_text(k.capitalize() + ':\t' + v + '\n', columns = 20, font = 'a')
            d.ln(2)

        d.cut()

        p._raw(d.output)


    except Exception as e:
        print(e)




def run_service(username, password, vendor_id = 0x04b8, product_id = 0x0e02, dummy = False):
    # initialize printer here
    if not dummy:
        p = None
        while p == None:
            try:
                p = Usb(vendor_id, product_id)

            except Exception as e:
                print(e)
                print("Trying again in 15 seconds")
                time.sleep(15)

    else:
        p = Dummy()



    can_order = True

    try:
        with IMAPClient(host="imap.gmail.com") as client:
            client.login(username, password)
            client.select_folder('INBOX')
            while can_order:
                new_messages = client.search([['FROM', 'cornellpikeskitchen@gmail.com']])
                for msgid, raw_email in client.fetch(new_messages, 'RFC822').items():
                    new_order = Order(msgid, raw_email)
                    new_order.print_order(p)

                client.delete_messages(new_messages)
                client.expunge()

                time.sleep(15)
                client.noop()

    except KeyboardInterrupt:
        # print_error_message(p, "Quitting. Restart Raspberry PI (black switch) to continue reading orders.")
        raise KeyboardInterrupt;

    except imapclient.exceptions.LoginError as e:
        print_error_message(p, "Could not connect to internet.")

    except Exception as e:
        print(e)
        #just try again after waiting
        time.sleep(15)
        run_service(username, password)


run_service(username, password)

# 87 - James Buzaid
#
