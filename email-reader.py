from imapclient import IMAPClient
import json, time
from schedule import Schedule
from datetime import datetime, date, timedelta
import queue
import email
from email import policy


username = input('Username: ')
password = input('Password: ')

def run_service(today, order_range, username, password):
    can_order = order_range[0] <= datetime.now().time() and (datetime.now() + timedelta(minutes = 2)).time() <= order_range[1]

    already_ordered = {}
    orders_to_print = queue.Queue()


    with IMAPClient(host="imap.gmail.com") as client:
        client.login(username, password)
        client.select_folder('INBOX')

        # get new messages, print them, then delete them
        while can_order:
            print("")
            print("Reading Orders")
            new_messages = client.search([['FROM', 'cornellpikesorders@gmail.com'], ['SINCE', today]])
            for msgid, raw_email in client.fetch(new_messages, 'RFC822').items():
                new_order = Order(msgid, raw_email)
                orders_to_print.put(new_order)
            client.delete_messages(new_messages)
            client.expunge()

            time.sleep(30)
            client.noop()

class Order:
    def __init__(self, msgid, raw_email):
        email_message = email.message_from_bytes(raw_email[b'RFC822'], policy = policy.default)
        body = str(email_message.get_body('text/plain'))
        body = body[body.find('{'): body.find('}') + 1]
        self.order_dict = json.loads(body)
        print(self.order_dict)
        self.date = email_message.get('Date')




run_service(date.today(), Schedule["kitchen_open"], username, password)
