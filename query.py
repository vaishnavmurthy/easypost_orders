import easypost
import csv
import sys
import json
from datetime import date
import math
from email_customer.email_customer import EmailCustomer

# FILL WITH TEST/PROD API KEY
with open("env_variables.json", 'r+') as file:
    env_variables = json.loads(file.read())
API_KEY = env_variables["APIKey"]
easypost.api_key = API_KEY

# Change to true when ready to buy labels
READY_TO_BUY = False


def email_tracking_number(customer_email, tracking_code):
    print(f"Emailing {tracking_code} to {customer_email}")
    email = EmailCustomer(customer_email, tracking_code)
    email.send_mail()


def initialize_params():
    header_row = ["cust_name", "cust_street", "cust_street2", "cust_city", "cust_state", "cust_zip", "cust_phone",
                  "to_residential", "length", "width", "height", "weight", "shipping_label_url", "tracking_number"]
    from_address_dict = {
        "name": "Chikfu",
        "company": "Chikfu",
        "street1": "12639 Coit Road",
        "street2": "#2216",
        "city": "Dallas",
        "state": "TX",
        "zip": "75251",
        "phone": "9154719427",
        "email": "contact@chikfu.co",
        "residential": None
    }
    to_address_list = []
    parcel_list = []
    with open(sys.argv[1], 'r') as file:
        data = file.read()
    order_list = json.loads(data)
    for order in order_list:
        order_dict = order
        if order_dict["fulfillmentStatus"] == "PENDING":
            temp_dict = order_dict["shippingAddress"]
            temp_dict["customerEmail"] = order_dict["customerEmail"]
            # calculate parcel dimensions based on quantity - up to 12 10x10x10, weight 2lb for 3 chikfu
            # + ice pack .5 lb + 3.5 lb per parcel
            order_quantity = order_dict["lineItems"][0]["quantity"]
            num_parcels = int(math.ceil(order_quantity/12))
            dimensions = str(num_parcels * 10)
            # play around with numbers for accuracy
            parcel_weight = num_parcels * 3.5
            chikfu_weight = order_quantity * 2/3
            ice_pack_weight = order_quantity / 2
            weight = str(int(math.ceil(parcel_weight + chikfu_weight + ice_pack_weight)))
            parcel_dict = {
                "length": dimensions,
                "width": dimensions,
                "height": dimensions,
                "weight": weight
            }
            temp_dict["parcel"] = parcel_dict
            to_address_list.append(temp_dict)
    return header_row, from_address_dict, to_address_list


if __name__ == '__main__':
    output_csv_file = f'{date.today()}-chikfu_orders.csv'
    param_list = initialize_params()
    header_row = param_list[0]
    from_address_dict = param_list[1]
    to_address_list = param_list[2]
    output_file = open(output_csv_file, 'w+')
    csvwriter = csv.writer(output_file)
    csvwriter.writerow(header_row)
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
            residential=None
        )
        # initializing parcel
        parcel = easypost.Parcel.create(
            length=to_address_dict["parcel"]["length"],
            width=to_address_dict["parcel"]["width"],
            height=to_address_dict["parcel"]["height"],
            weight=to_address_dict["parcel"]["weight"]
        )

        # creating shipment
        shipment = easypost.Shipment.create(
            to_address=toAddress,
            from_address=fromAddress,
            parcel=parcel
        )
        LSO_flag = 0
        chosen_rate = {}
        print(shipment)
        # ensuring LSO rates are available
        for rate in shipment.rates:
            if rate["carrier"] == 'LSO' and rate["service"] == "ECommerce":
                chosen_rate = rate
                LSO_flag = 1
                break
        if not LSO_flag:
            print("[!] Unable to pull LSO rates")
            continue
        # Only completes purchase when ready
        if READY_TO_BUY:
            try:
                print(f"Buying shipment:")
                shipment.buy(rate=chosen_rate)
                print(f"URL: {shipment.postage_label.label_url}")
                print(f"Tracking code: {shipment.tracking_code}")
                print(f"Emailing tracking number {to_address_dict['customerEmail']}...")
                email_tracking_number(to_address_dict['customerEmail'], shipment.tracking_code)
                line.append(shipment.postage_label.label_url)
                line.append(shipment.tracking_code)
                csvwriter.writerow(line)
            except Exception as e:
                print(f"[!] Not able to complete purchase of label - {e}")
                continue
