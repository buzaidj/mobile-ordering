from imapclient import IMAPClient
import json, time
from datetime import datetime, date, timedelta
import queue
import email
from email import policy

import printing
import schedule

username = input('Username: ')
password = input('Password: ')

class Order:
    """
    Class to represent an order and print them
    """
    def __init__(self, msgid, raw_email):
        """
        Initializes an order from a raw email and msg id
        """
        email_message = email.message_from_bytes(raw_email[b'RFC822'], policy = policy.default)
        body = str(email_message.get_body('text/plain'))
        body = body[body.find('{'): body.find('}') + 1]

        self.order_number = msgid
        self.can_print = True

        try:
            self.order_dict = json.loads(body)
        except:
            self.order_dict = {}
            self.can_print = False

        self.date = email_message.get('Date')

    def print_order(self):
        printing.print_line("Order #", self.order_number)
        if self.can_print:
            for k, v in self.order_dict.items():
                printing.print_line(k, v)
        else:
            printing.print_text_line("Order not formatted correctly")

        printing.print_blank()



def run_service(today, orderTimes, username, password):
    can_order = orderTimes.order_range[0] <= datetime.now().time() and (datetime.now() + timedelta(minutes = 2)).time() <= orderTimes.order_range[1]

    already_ordered = {}


    with IMAPClient(host="imap.gmail.com") as client:
        client.login(username, password)
        client.select_folder('INBOX')

        # get new messages, print them, then delete them
        while can_order:
            print("")
            print("Reading Orders")
            new_messages = client.search([['FROM', 'cornellpikesorders@gmail.com']])
            for msgid, raw_email in client.fetch(new_messages, 'RFC822').items():
                new_order = Order(msgid, raw_email)
                new_order.print_order()

            client.delete_messages(new_messages)
            client.expunge()

            time.sleep(30)
            client.noop()

run_service(date.today(), schedule.Schedule["test_full"], username, password)
