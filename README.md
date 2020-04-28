# easypost_orders
Python script to generate shipping labels and tracking information using the EasyPost API  

## Features:
* Generates shipping labels and tracking numbers for a given carrier
* Emails customer the tracking number once generated

## Install requirements
`pip install -r requirements.txt`

## Create Config File
Config file is a json file named `env_variables.json` that contains the API key, the brand email and password.  

Structure of the file is the following:
```
{
  "EmailUsername": "companyemail@example.com",
  "EmailPassword": "PASSWORD",
  "APIKey": "xxyyzzz"
}
```

## CSV / JSON file
* The script takes in either the default output order csv from SquareSpace, or the order json object 
from the SquareSpace API as input.
* Place either type of file in the *Orders* directory and update the `SQUARESPACE` variable in `main.py` accordingly.

## Usage
`python main.py`  

## Outputs  
The script will create the following outputs:  
* An output csv file containing order details, the url of the label, and the tracking code will be placed in the 
*OutputFiles* folder.
    * File will be named `<TODAY'S_DATE>-chikfu_orders.csv`.
* An email with the tracking number will be sent from the email address included in `env_variables.json`.
    * The content of the email will be controlled by `email_customer/email_template.html`.
* Shipping labels in JPG format will be placed in the *Labels* folder. 
    * Labels will be named `<TODAY'S_DATE>-<CUSTOMER'S_NAME>-label.jpg`.