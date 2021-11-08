
# Description
---
skyflow-python is the Skyflow SDK for the Python programming language.

## Usage
---
You can install the package using the following command:


```bash
$ pip install skyflow
```

## Table of Contents

* [Service Account Token Generation](#service-account-token-generation)  
* [Vault APIs](#vault-apis)
  * [Insert](#insert)
  * [Detokenize](#detokenize)
  * [GetById](#get-by-id)
  * [InvokeConnection](#invoke-connection)

### Service Account Token Generation

The [Service Account](https://github.com/skyflowapi/skyflow-python/tree/main/ServiceAccount) python module is used to generate service account tokens from service account credentials file which is downloaded upon creation of service account. The token generated from this module is valid for 60 minutes and can be used to make API calls to vault services as well as management API(s) based on the permissions of the service account.

[Example](https://github.com/skyflowapi/skyflow-python/blob/main/examples/SATokenExample.py):


```python
from skyflow.ServiceAccount import GenerateToken

filepath =  '<YOUR_CREDENTIALS_FILE_PATH>'
accessToken, tokenType = GenerateToken(filepath)

print("Access Token:", accessToken)
print("Type of token:", tokenType)
```

### Vault APIs
The [Vault](https://github.com/skyflowapi/skyflow-python/tree/main/Vault) python module is used to perform operations on the vault such as inserting records, detokenizing tokens, retrieving tokens for a skyflow_id and to invoke a connection.

To use this module, the skyflow client must first be initialized as follows.

```python
from skyflow.Vault import Client, Configuration
from skyflow.ServiceAccount import GenerateToken

#User defined function to provide access token to the vault apis
def tokenProvider():    
    token, _ = GenerateToken('<YOUR_CREDENTIALS_FILE_PATH>')
    return token

#Initializing a Skyflow Client instance with a SkyflowConfiguration object
config = Configuration('<YOUR_VAULT_ID>', '<YOUR_VAULT_URL>', tokenProvider)
client = Client(config) 
```

All Vault APIs must be invoked using a client instance.

#### Insert
To insert data into the vault from the integrated application, use the insert(records: dict, options: InsertOptions) method of the Skyflow client. The records parameter takes an array of records to be inserted into the vault. The options parameter takes a Skyflow.InsertOptions object. See below:

```python
from skyflow.Vault import InsertOptions

#Initialize Client
try:
    options = InsertOptions(True) #indicates whether or not tokens should be returned for the inserted data. Defaults to 'True'

    data = {
        "records": [
            {
                "table": "<TABLE_NAME>",
                "fields": {
                    "<FIELDNAME>": "<VALUE>"
                }
            }
        ]
    }
    response = client.insert(data, options=options)
    print('Response:', response)
except SkyflowError as e:
    print('Error Occured:', e)
```

An example of an insert call is given below:

```python
client.insert(
    {
        "records": [
            {
                "table": "cards",
                "fields": {
                    "cardNumber": "41111111111",
                    "cvv": "123",
                },
            }
        ]
    },
    InsertOptions(True),
)
```

Sample response :
```python
{
    "records": [
        {
            "table": "cards",
            "fields": {
                "cardNumber": "f3907186-e7e2-466f-91e5-48e12c2bcbc1",
                "cvv": "1989cb56-63da-4482-a2df-1f74cd0dd1a5",
            },
        }
    ]
}
```

#### Detokenize

For retrieving using tokens, use the detokenize(records: dict) method. The records parameter takes a dictionary that contains records to be fetched as shown below.

```python
{
  "records":[
    {
      "token": "string"     #token for the record to be fetched
    }
  ]
}
```

An example of a detokenize call:

```python
client.detokenize(
    {"records": [{"token": "45012507-f72b-4f5c-9bf9-86b133bae719"}]}
)
```

Sample response:

```python
{
  "records": [
    {
      "token": "131e70dc-6f76-4319-bdd3-96281e051051",
      "value": "1990-01-01"
    }
  ]
}
```

#### Get By Id

For retrieving using SkyflowID's, use the getById(records: dict) method. The records parameter takes a Dictionary that contains records to be fetched as shown below:

```python
{
    "records": [
        {
            "ids": list<str>,  # List of SkyflowID's of the records to be fetched
            "table": str,  # name of table holding the above skyflow_id's
            "redaction": Skyflow.RedactionType,  # redaction to be applied to retrieved data
        }
    ]
}
```

There are 4 accepted values in Skyflow.RedactionTypes:  
- `PLAIN_TEXT`
- `MASKED`
- `REDACTED`
- `DEFAULT` 

An example of getById call:

```python
from skyflow.Vault import RedactionType

skyflowIDs = [
    "f8d8a622-b557-4c6b-a12c-c5ebe0b0bfd9",
    "da26de53-95d5-4bdb-99db-8d8c66a35ff9",
]
record = {"ids": skyflowIDs, "table": "cards", "redaction": RedactionType.PLAIN_TEXT}

invalidID = ["invalid skyflow ID"]
badRecord = {"ids": invalidID, "table": "cards", "redaction": RedactionType.PLAIN_TEXT}

records = {"records": [record, badRecord]}

client.getById(records)
```

Sample response:
```python
{
  "records": [
      {
          "fields": {
              "card_number": "4111111111111111",
              "cvv": "127",
              "expiry_date": "11/35",
              "fullname": "myname",
              "skyflow_id": "f8d8a622-b557-4c6b-a12c-c5ebe0b0bfd9"
          },
          "table": "cards"
      },
      {
          "fields": {
              "card_number": "4111111111111111",
              "cvv": "317",
              "expiry_date": "10/23",
              "fullname": "sam",
              "skyflow_id": "da26de53-95d5-4bdb-99db-8d8c66a35ff9"
          },
          "table": "cards"
      }
  ],
  "errors": [
      {
          "error": {
              "code": "404",
              "description": "No Records Found"
          },
          "skyflow_ids": ["invalid skyflow id"]
      }
  ]
}
```

#### Invoke Connection
Using Skyflow Connection, end-user applications can integrate checkout/card issuance flow with their apps/systems. To invoke connection, use the invokeConnection(config: Skyflow.ConnectionConfig) method of the Skyflow client.

```python
connectionConfig = ConnectionConfig(
  connectionURL: String, # connection url received when creating a skyflow connection integration
  methodName: Skyflow.RequestMethod,
  pathParams: [String: Any],	# optional
  queryParams: [String: Any],	# optional
  requestHeader: [String: String], # optional
  requestBody: [String: Any],	# optional
)
client.invokeConnection(connectionConfig)
```

`methodName` supports the following methods:
- GET
- POST
- PUT
- PATCH
- DELETE

**pathParams, queryParams, requestHeader, requestBody** are the JSON objects represented as dictionaries that will be sent through the connection integration url.

An example of invokeConnection:
```python
from skyflow.Vault import ConnectionConfig, Configuration, RequestMethod

def tokenProvider():
    token, _ = GenerateToken('<YOUR_CREDENTIALS_FILE_PATH>')
    return token

try:
    config = Configuration('<YOUR_VAULT_ID>', '<YOUR_VAULT_URL>', tokenProvider)
    connectionConfig = ConnectionConfig('<YOUR_CONNECTION_URL>', RequestMethod.POST,
    requestHeader={
                'Content-Type': 'application/json',
                'Authorization': '<YOUR_CONNECTION_BASIC_AUTH>'
    },
    requestBody= # For third party integration
    {
        "expirationDate": {
            "mm": "12",
            "yy": "22"
        }
    },
    pathParams={'cardID': '<CARD_VALUE>'}) # param as in the example
    client = Client(config)

    response = client.invokeConnection(connectionConfig)
    print('Response:', response)
except SkyflowError as e:
    print('Error Occured:', e)
```

Sample response:
```python
{
    "receivedTimestamp": "2021-11-05 13:43:12.534",
    "processingTimeinMs": 12,
    "resource": {
        "cvv2": "558"
    }
}
```