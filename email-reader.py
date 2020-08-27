from imapclient import IMAPClient
import imapclient.exceptions
import json, time
from datetime import datetime, date, timedelta, timezone
import queue
import email
from email import policy
from smtplib import SMTP_SSL as SMTP       # this invokes the secure SMTP protocol (port 465, uses SSL)
from email.mime.text import MIMEText

import sys
import os
import re

import pytz
from tzlocal import get_localzone
import phonenumbers
from escpos.printer import Usb, Dummy

"""
Class to keep track of a printer and the orders already printed without a USB connection
"""

class DummyPrinter:
    def __init__(self):
        self.d = Dummy()
    # TODO: find a way to clear out this set

    def print_ticket(self, order):
        self.d.line_spacing(120)
        self.d.ln(1)

        self.d.set(align = "center", bold = True, underline = 2, double_height = False, double_width = False, custom_size = True, smooth = True, width = 2, height = 2, invert = False, density = 8, font = 'a')
        self.d.block_text(str(order.order_number) + ' ' + order.name + '\n', font = 'a')
        self.d.ln(1)

        self.d.set(align = "center", bold = False, underline = 0, double_height = False, double_width = False, custom_size = True, smooth = True, width = 2, height = 2, invert = False, density = 8, font = 'a')
        self.d.block_text(order.order_type + '\n', columns = 20, font = 'a')
        self.d.ln(1)

        self.d.text(order.formatted_number + '\n')
        self.d.text(order.date + '\n')
        self.d.text(order.time + '\n')
        self.d.text(' \n')

        self.d.set(align = "left", bold = True, underline = 0, double_height = False, double_width = False, custom_size = True, smooth = True, width = 2, height = 2, invert = False, density = 8, font = 'b')
        self.d.text('PICKUP TIME\n')

        self.d.set(align = "left", bold = False, underline = 0, double_height = False, double_width = False, custom_size = True, smooth = True, width = 2, height = 2, invert = False, density = 8, font = 'a')
        self.d.block_text(order.pickup_time + '\n', columns = 20, font = 'a')

        self.d.set(align = "left", bold = True, underline = 0, double_height = False, double_width = False, custom_size = True, smooth = True, width = 2, height = 2, invert = False, density = 8, font = 'b')
        self.d.text('ORDER\n')

        self.d.set(align = "left", bold = False, underline = 0, double_height = False, double_width = False, custom_size = True, smooth = True, width = 2, height = 2, invert = False, density = 8, font = 'a')
        self.d.block_text(order.order + '\n', columns = 20, font = 'a')

        self.d.ln(2)

        if order.notes != '':
            self.d.set(align = "left", bold = True, underline = 0, double_height = False, double_width = False, custom_size = True, smooth = True, width = 2, height = 2, invert = False, density = 8, font = 'b')
            self.d.text('NOTES\n')

            self.d.set(align = "left", bold = False, underline = 0, double_height = False, double_width = False, custom_size = True, smooth = True, width = 2, height = 2, invert = False, density = 8, font = 'a')
            self.d.block_text(order.notes + '\n', columns = 20, font = 'a')

        self.d.cut()

        print('PRINTED ORDER')

    def print_ticket_limited(self, order):
        self.d.line_spacing(120)

        self.d.set(align = "center", bold = True, underline = 2, double_height = False, double_width = False, custom_size = True, smooth = True, width = 2, height = 2, invert = False, density = 8, font = 'a')
        self.d.block_text(str(order.order_number) + ' ' + '\n', font = 'a')
        self.d.ln(1)

        self.d.set(align = "center", bold = False, underline = 0, double_height = False, double_width = False, custom_size = True, smooth = True, width = 2, height = 2, invert = False, density = 8, font = 'a')
        self.d.block_text(order.order_type + '\n', columns = 20, font = 'a')
        self.d.ln(1)

        self.d.text(order.order_date + '\n')
        self.d.text(order.order_time + '\n')
        self.d.text(' \n')


        self.d.set(align = "left", bold = True, underline = 0, double_height = False, double_width = False, custom_size = True, smooth = True, width = 2, height = 2, invert = False, density = 8, font = 'b')
        self.d.text('ORDER DETAILS\n')

        self.d.set(align = "left", bold = False, underline = 0, double_height = False, double_width = False, custom_size = True, smooth = True, width = 2, height = 2, invert = False, density = 8, font = 'a')
        for k, v in order.order_dict.items():
            self.d.block_text(k.capitalize() + ':\t' + v + '\n', columns = 20, font = 'a')
            d.ln(2)

        d.cut()


    def print_ticket_limited(self, order):
        pass

        # TODO: make this work for misformatted ordders


    def print_error_message(self, error_message):
        pass

"""
Inherits the DummyPrinter class for a not connected printer
"""
class UsbPrinter(DummyPrinter):
    """
    Initialize USB printer with vendor ID and product ID
    """
    def __init__(self, vendor_id = 0x04b8, product_id = 0x0e02):
        super().__init__()
        self.p = None
        while self.p == None:
            try:
                self.p = Usb(vendor_id, product_id)

            except Exception as e:
                print(e)
                print("Trying again in 15 seconds")
                time.sleep(15)

    def print_ticket(self, order):
        super(self, order)
        self.p._raw(d.output)



"""
Class to represent an order


ALL ORDERS HAVE:
:param order_type: str
:param order_number: int
:param can_print: bool
:param dt: dt
:param date: str
:param time: str

WORKING ORDERS HAVE
:param order_dict: dict
:param name: str
:param number: str
:param formatted_number: str
:param order: str
:param notes: str
:param pickup_time_dt: dt
:param pickup_time: str

"""
class Order:
    needed_params = ['Name', 'Number', 'Order', 'Notes', 'Pickup Time', 'Email']

    email_time_format = '%a, %d %b %Y %H:%M:%S %z'
    date_format = "%b %-d"
    time_format = "%-I:%M:%S %p"
    pickup_time_format = "%a %b %d %Y %H:%M:%S"
    pickup_time_print_format = "%-I:%M %p"

    def __init__(self, msgid, raw_email):
        email_message = email.message_from_bytes(raw_email[b'RFC822'], policy = policy.default)
        self.order_type = email_message.get('Subject')
        self.body = str(email_message.get_body('text/plain'))
        self.body = self.body[self.body.find('{'): self.body.find('}') + 1]
        self.body = self.body.replace('\n', '')
        self.order_number = msgid % 100

        self.can_print = 'full'
        try:
            self.order_dict = json.loads(self.body)
            try:
                for x in self.needed_params:
                    assert x in self.order_dict

                self.name = self.order_dict.pop('Name')
                self.number = self.order_dict.pop('Number')

                try:
                    self.formatted_number = phonenumbers.format_number(phonenumbers.parse(number, 'US'), phonenumbers.PhoneNumberFormat.NATIONAL)
                except:
                    self.formatted_number = "Could not parse phone number"

                self.order = self.order_dict.pop('Order')
                self.notes = self.order_dict.pop('Notes')
                self.email = self.order_dict.pop('Email')

                pickup_time_str = self.order_dict.pop('Pickup Time')
                x = pickup_time_str.find('GMT')
                pickup_time_str = pickup_time_str[:x-1]

                self.pickup_time_dt = datetime.strptime(pickup_time_str, self.pickup_time_format)
                self.pickup_time = self.pickup_time_dt.strftime(self.pickup_time_print_format)

            except Exception as e:
                print(e)
                self.can_print = 'limited'
                # SECONDARY PRINTING OF MISFORMATTED MESSAGE THAT CAN STILL BE READ
        # add back later
        except Exception as e:
            self.order_dict = {}
            self.can_print = 'message format error'
            print(e)

        try:
            dt_str = str(email_message.get('Date'))
            self.dt = datetime.strptime(dt_str, self.email_time_format).astimezone(self.tz)
            self.date = self.dt.strftime(self.date_format)
            self.time = self.dt.strftime(self.time_format)
        except:
            self.dt = datetime.now()
            self.date = self.dt.strftime(self.date_format)
            self.time = self.dt.strftime(self.time_format)

    """
    Gets confirmation email contents
    """
    def get_confirmation_email(self):
        if self.can_print == 'full':
            email_content = 'Your order has been confirmed.\n\n'
            email_content += 'Order:\t' + self.order
            email_content += 'Pickup time:\t' + self.pickup_time
            destination = [self.email]

        elif self.can_print == 'limited':
            email_content = 'Your order has been confirmed.\n\n'
            destination = [self.order_dict.get('Email')]
            if destination == [None]:
                return False
        else:
            return False

        return destination, email_content

    def __eq__(self, other):
        return self.body == other.body

    def __hash__(self):
        return hash(self.body)

class OutgoingEmail:
    def __init__(self, username, password):
        SMTPserver = 'smtp.gmail.com'
        port_num = 465

        self.sender = username
        self.text_subtype = 'plain'

        self.conn = SMTP(SMTPserver)
        self.conn.set_debuglevel(False)
        self.conn.login(username, password)

    def send_email(self, destination, msg_content):
        msg = MIMEText(msg_content, self.text_subtype)
        msg['Subject'] = 'PIKE - Order Confirmation'
        msg['From'] = self.sender

        try:
            self.conn.sendmail(sender, destination, msg.as_string())
        except Exception as e:
            return False
            print(e)
        finally:
            self.conn.quit()
            return True


"""
An entry with a time on it so that older entries can be removed from the set
"""
class TimedOrderEntry:
    def __init__(self, order):
        self.order = order
        self.time = datetime.now

    def __eq__(self, other):
        return self.order.body == other.order.body

    def __hash__(self):
        return hash(self.order)

"""
Manages reading of emails, passes
"""
class EmailPrinterManager:
    """
    Initialize manager
    """
    def __init__(self, incoming_username, incoming_password, outgoing_username, outgoing_password, dummy = False):
        if dummy:
            self.printer = DummyPrinter()
        else:
            self.printer = UsbPrinter()

        self.incoming_username = incoming_username
        self.incoming_password = incoming_password

        self.outgoing_username = outgoing_username
        self.outgoing_password = outgoing_password

        # self.can_order = orderTimes.order_range[0] <= datetime.now().time() and (datetime.now() + timedelta(minutes = 2)).time() <= orderTimes.order_range[1]
        self.already_printed = set()

        self.last_refresh = datetime.now()


    """
    Decides which printer to print from, returns True on a successful print
    """
    def print_order(self, order):
        if order.can_print == 'full':
            self.printer.print_ticket(order)
            return True

        elif order.can_print == 'limited':
            self.printer.print_ticket_limited(order)
            return True

        else:
            self.printer.print_error_message(order.can_print)
            return False


    """
    Removes old entries from the already_printed set
    """
    def refresh(self):
        new_set = {}
        now = datetime.now()
        for timedOrderEntry in self.already_printed:
            if timedOrderEntry.time > now - timedelta(days = 1): # new enough
                new_set.append(timedOrderEntry)

        self.already_printed = new_set

    """
    Actively reads inbox, returns true if it was successful and calls order's send confirmationi email to send email
    """
    def read_emails(self):
        while True:
            try:
                with IMAPClient(host="imap.gmail.com") as client:
                    client.login(self.incoming_username, self.incoming_password)
                    client.select_folder('INBOX')
                    while True:
                        new_messages = client.search([['FROM', 'cornellpikeskitchen@gmail.com']])
                        for msgid, raw_email in client.fetch(new_messages, 'RFC822').items():
                            order = Order(msgid, raw_email)
                            print(not order in self.already_printed)
                            if not order in self.already_printed:
                                printed_successfuly = self.print_order(order)
                                if printed_successfuly:
                                    self.already_printed.add(order)
                                    outgoing_email_client = OutgoingEmail(self.outgoing_username, self.outgoing_password)
                                    dest, email_content = order.get_confirmation_email()
                                    outgoing_email_client.send_email(dest, email_content)

                        client.delete_messages(new_messages)
                        client.expunge()

                        if self.last_refresh + timedelta(hours = 1) < datetime.now(): # resets set by removing old entries
                            self.refresh()

                        time.sleep(15)
                        client.noop()

                return

            except Exception as e:
                self.printer.print_error_message(e)
                print(e)
                #just try again after waiting
                time.sleep(15)


"""
Scheudles execution of lunch, dinner, and brunch
"""
class TaskScheduler:
    incoming_username = ''
    incoming_password = ''

    outgoing_username = ''
    outgoing_password = ''

    dummy = True

    def __init__(self):
        while True:
            manager = EmailPrinterManager(self.incoming_username, self.incoming_password, self.outgoing_username, self.outgoing_password, self.dummy)
            manager.read_emails()
            time.sleep(120) # wait and try again

TaskScheduler()
