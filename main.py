import csv
import json
import os
import urllib.request
from datetime import date

import easypost

from email_customer.email_customer import EmailCustomer
from initialize.initialize import Initialize

with open("env_variables.json", 'r+') as file:
    env_variables = json.loads(file.read())
API_KEY = env_variables["APIKey"]
easypost.api_key = API_KEY

# Change to true when ready to buy labels
READY_TO_BUY = False

# Change to true when ready to use SquareSpace API
SQUARESPACE = False


def email_tracking_number(customer_email, tracking_code):
    print(f"[+] Emailing {tracking_code} to {customer_email}")
    email = EmailCustomer(customer_email, tracking_code)
    email.send_mail()


if __name__ == '__main__':
    output_csv_file = f'OutputFiles{os.sep}{date.today()}-chikfu_orders.csv'
    print("[+] Initializing parameters")
    parameters = Initialize(SQUARESPACE)
    header_row = parameters.header_row
    if READY_TO_BUY:
        output_file = open(output_csv_file, 'w+')
        csvwriter = csv.writer(output_file)
        csvwriter.writerow(header_row)
    from_address_dict = parameters.from_address_dict
    to_address_list = parameters.to_address_list
    for to_address_dict in to_address_list:
        # Adding customer / parcel details to csv row
        line = [
            to_address_dict["firstName"] + " " + to_address_dict["lastName"],
            to_address_dict["address1"],
            to_address_dict["address2"],
            to_address_dict["city"],
            to_address_dict["state"],
            to_address_dict["postalCode"],
            to_address_dict["phone"],
            to_address_dict["customerEmail"],
            to_address_dict["parcel"]["length"],
            to_address_dict["parcel"]["width"],
            to_address_dict["parcel"]["height"],
            to_address_dict["parcel"]["weight"]
        ]
        # initializing from address
        fromAddress = easypost.Address.create(
            name=from_address_dict["name"],
            company=from_address_dict["company"],
            street1=from_address_dict["street1"],
            street2=from_address_dict["street2"],
            city=from_address_dict["city"],
            state=from_address_dict["state"],
            zip=from_address_dict["zip"],
            phone=from_address_dict["phone"],
            email=from_address_dict["email"],
            residential=from_address_dict["residential"]
        )
        # initializing to address
        # NOTE: by default residential is assumed
        toAddress = easypost.Address.create(
            name=to_address_dict["firstName"] + " " + to_address_dict["lastName"],
            street1=to_address_dict["address1"],
            street2=to_address_dict["address2"],
            city=to_address_dict["city"],
            state=to_address_dict["state"],
            zip=to_address_dict["postalCode"],
            phone=to_address_dict["phone"],
            email=to_address_dict["customerEmail"],
            residential=False
        )

        # initializing parcel
        parcel = easypost.Parcel.create(
            length=to_address_dict["parcel"]["length"],
            width=to_address_dict["parcel"]["width"],
            height=to_address_dict["parcel"]["height"],
            weight=to_address_dict["parcel"]["weight"]
        )
        # creating shipment filtering on LSO carrier account
        shipment = easypost.Shipment.create(
            to_address=toAddress,
            from_address=fromAddress,
            parcel=parcel,
            carrier_accounts=["ca_fd3f3bb2d9db4e40a8555f5aba3d0c6f"]
        )
        LSO_flag = 0
        chosen_rate = {}
        simple_ground_rate = {}
        # ensuring LSO rates are available
        for rate in shipment.rates:
            if rate["carrier"] == 'LSO' and rate["service"] == "ECommerce":
                chosen_rate = rate
                LSO_flag = 1
                break
            elif rate["carrier"] == "LSO" and rate["service"] == "SimpleGroundBasic":
                LSO_flag = 1
                simple_ground_rate = rate
        if not LSO_flag:
            print(f"[!] Unable to pull LSO ECommerce or GroundBasic rate for {toAddress.name}")
            for rate in shipment.rates:
                print(rate)
            continue
        elif chosen_rate == {}:
            chosen_rate = simple_ground_rate
        # Only completes purchase when ready
        print(f"[+] Chosen rate for purchase for {toAddress.name}: {chosen_rate['carrier']} {chosen_rate['service']}")
        if READY_TO_BUY:
            try:
                print(f"[+] Buying shipment:")
                shipment.buy(rate=chosen_rate)
                print(f"[+] URL: {shipment.postage_label.label_url}")
                # downloading label to Labels directory
                urllib.request.urlretrieve(shipment.postage_label.label_url,
                                           f"Labels{os.sep}{date.today()}-{toAddress.name.replace(' ', '_')}-label.jpg")
                print(f"[+] Tracking code: {shipment.tracking_code}")
                print(f"[+] Emailing tracking number {to_address_dict['customerEmail']}...")
                email_tracking_number(to_address_dict['customerEmail'], shipment.tracking_code)
                line.append(shipment.postage_label.label_url)
                line.append(shipment.tracking_code)
                csvwriter.writerow(line)
            except Exception as e:
                print(f"[!] Not able to complete purchase of label - {e}")
                continue
