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
from the SquareSpace API as input
* Place either type of file in the *Orders* directory and update the `SQUARESPACE` variable in `main.py` accordingly

## Usage
`python main.py`