# easypost_orders
Python script to generate shipping labels and tracking information using the EasyPost API

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

## Usage
`python query.py PATH_TO_SQUARESPACE_JSON`

OR

`python query.py PATH_TO_ORDER_CSV_FILE`
