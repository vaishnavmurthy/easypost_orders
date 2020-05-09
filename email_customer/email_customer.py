import json
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template


class EmailCustomer:

    def __init__(self, customer_email, tracking_number):
        self.tracking_number = tracking_number
        self.customer_email = customer_email
        self.text_message = f"\nHello valued customer,\n" \
                            f"Thank you for your Chikfu order! It will be shipped shortly.\n" \
                            f"Your tracking number is {self.tracking_number}\n" \
                            f"Best,\n" \
                            f"Chikfu Team"
        with open("email_customer/email_template.html", "r") as file:
            html_message = file.read()
        template = Template(html_message)
        self.html_message = template.substitute(tracking_number=self.tracking_number)

    def send_mail(self):
        # initialize server
        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context)
        with open("env_variables.json", "r") as file:
            env_variables = json.loads(file.read())
        # pulling username and password from config file
        username = env_variables["EmailUsername"]
        password = env_variables["EmailPassword"]
        # logging into server
        server.login(username, password)
        message = MIMEMultipart("alternative")
        message["Subject"] = "Your Chikfu Order"
        message["From"] = username
        message["To"] = self.customer_email
        # adding in both plain text and html options in cases where email clients do not support html email
        part1 = MIMEText(self.text_message, "plain")
        part2 = MIMEText(self.html_message, "html")
        message.attach(part1)
        message.attach(part2)
        # sending email
        server.sendmail(username, self.customer_email, message.as_string())
