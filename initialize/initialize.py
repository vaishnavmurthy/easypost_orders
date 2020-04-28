import json
import math
import csv
import os


def calc_parcel_dict(order_quantity):
    num_parcels = int(math.ceil(order_quantity / 12))
    dimensions = "10"
    # play around with numbers for accuracy
    # calculate parcel dimensions based on quantity - up to 12 10x10x10, weight 2lb for 3 chikfu
    # + ice pack .5 lb + 3.5 lb per parcel
    parcel_weight = num_parcels * 2
    chikfu_weight = order_quantity * 9 / 16
    ice_pack_weight = order_quantity / 4
    weight = str(int(math.ceil((parcel_weight + chikfu_weight + ice_pack_weight) / num_parcels)))
    parcel_dict = {
        "length": dimensions,
        "width": dimensions,
        "height": dimensions,
        "weight": weight
    }
    parcel_list = []
    for i in range(num_parcels):
        parcel_list.append(parcel_dict)
    return parcel_list


class Initialize:
    def __init__(self, squarespace):
        self.squarespace = squarespace
        self.header_row = ["cust_name", "cust_street", "cust_street2", "cust_city", "cust_state", "cust_zip",
                           "cust_phone", "to_residential", "length", "width", "height", "weight", "shipping_label_url",
                           "tracking_number"
                           ]
        self.from_address_dict = {
            "name": "Chikfu",
            "company": "Chikfu",
            "street1": "12639 Coit Rd",
            "street2": "#2216",
            "city": "Dallas",
            "state": "TX",
            "zip": "75251",
            "phone": "9154719427",
            "email": "contact@chikfu.co",
            "residential": False
        }
        self.to_address_list = []
        if self.squarespace:
            print("[+] Reading shipping addresses from SquareSpace API JSON")
            self.initialize_to_address_squarespace()
        else:
            print("[+] Reading shipping addresses from SquareSpace order CSV file")
            self.initialize_to_address_csv()

    def initialize_to_address_csv(self):
        for directory, sub_dir, files in os.walk('Orders'):
            for file_name in files:
                if file_name[:4] == "done" or os.path.splitext(file_name)[1] != ".csv":
                    print(f"[!] Skipping file {file_name}")
                    continue
                with open(os.path.join(directory, file_name), 'r') as file:
                    csv_reader = csv.reader(file)
                    for line in csv_reader:
                        fulfillment = line[4]
                        if fulfillment.upper() == "PENDING":
                            temp_dict = {}
                            billing_name = line[24]
                            first_name = billing_name.split(" ")[0]
                            last_name = billing_name.split(" ")[-1]
                            address1 = line[33].strip()
                            address2 = line[34].strip()
                            city = line[35]
                            postal_code = line[36]
                            state = line[37]
                            customer_email = line[1]
                            phone = line[39]
                            order_quantity = int(line[16])
                            parcel_list = calc_parcel_dict(order_quantity)
                            for parcel_dict in parcel_list:
                                temp_dict["firstName"] = first_name
                                temp_dict["lastName"] = last_name
                                temp_dict["address1"] = address1
                                temp_dict["address2"] = address2
                                temp_dict["city"] = city
                                temp_dict["postalCode"] = postal_code
                                temp_dict["state"] = state
                                temp_dict["customerEmail"] = customer_email
                                temp_dict["phone"] = phone
                                temp_dict["parcel"] = parcel_dict
                                self.to_address_list.append(temp_dict)
                new_filename = "done-"+file_name
                os.rename(os.path.join(directory, file_name), os.path.join(directory, new_filename))

    def initialize_to_address_squarespace(self):
        for file_name in os.walk('../Orders'):
            if file_name[2][0][:4] == "done" or os.path.splitext(file_name[2][0]) != ".json":
                continue
            with open(file_name[2][0], 'r') as file:
                data = file.read()
            order_list = json.loads(data)
            for order in order_list:
                order_dict = order
                if order_dict["fulfillmentStatus"] == "PENDING":
                    temp_dict = order_dict["shippingAddress"]
                    temp_dict["customerEmail"] = order_dict["customerEmail"]
                    order_quantity = order_dict["lineItems"][0]["quantity"]
                    temp_dict["parcel"] = calc_parcel_dict(order_quantity)
                    self.to_address_list.append(temp_dict)
            new_filename = "done-" + file_name[2][0]
            os.rename(os.path.join(file_name[0], file_name[2]), os.path.join(file_name[0], new_filename))
