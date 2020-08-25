# https://stackoverflow.com/questions/64505/sending-mail-from-python-using-smtp <- credit to the top answer for setup help
import sys
import os
import re
import time

from smtplib import SMTP_SSL as SMTP       # this invokes the secure SMTP protocol (port 465, uses SSL)
# from smtplib import SMTP                  # use this for standard SMTP protocol   (port 25, no encryption)

# old version
# from email.MIMEText import MIMEText
from email.mime.text import MIMEText

USERNAME = input('Username: ')
PASSWORD = input('Password: ')

# USERNAME = input("Username/sender: ")
# PASSWORD = input("Password: ")

def send_email(content):

    SMTPserver = 'smtp.gmail.com'
    port_num = 465

    destination = ['cornellpikeskitchen@gmail.com']

    sender = USERNAME

    text_subtype = 'plain'

    subject="Lunch Order"

    msg = MIMEText(content, text_subtype)
    msg['Subject']=       subject
    msg['From']   = sender # some SMTP servers will do this automatically, not all

    conn = SMTP(SMTPserver)
    conn.set_debuglevel(False)
    conn.login(USERNAME, PASSWORD)
    try:
        conn.sendmail(sender, destination, msg.as_string())
    finally:
        conn.quit()

    time.sleep(5)

# content = """\
# {
#   "Name": "James Buzaid",
#   "Order": "Avocado Pepper Jack Bacon Burger Long Name",
#   "Number": "914 327 7539",
#   "Notes": "None",
#   "_": "this is a test order"
# }
# """
#
# send_email(content)

content = """\
{
  "naasdfme": "James Buzaid",
  "Order": "Avocado Pepper Jack Bacon Burger Long Name",
  "Number": "914 327 7539",
  "Notes": "None",
  "_": "this is a test order"
}
"""

send_email(content)
