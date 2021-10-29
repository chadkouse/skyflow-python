import json

import requests
from requests.models import HTTPError
from skyflow.Errors._skyflowErrors import SkyflowError, SkyflowErrorCodes, SkyflowErrorMessages


def getInsertRequestBody(data):
    try:
        records = data["records"]
    except KeyError:
        raise SkyflowError(SkyflowErrorCodes.INVALID_INPUT, SkyflowErrorMessages.RECORDS_KEY_ERROR)
    requestBody = {"records": []}
    for record in records:
        tableName, fields = getTableAndFields(record)
        requestBody["records"].append({
            "tableName": tableName,
            "fields": fields,
            "method": "POST",
            "quorum": True})
    try:
        jsonBody = json.dumps(requestBody)
    except Exception as e:
        raise SkyflowError(SkyflowErrorCodes.INVALID_INPUT ,SkyflowErrorMessages.INVALID_JSON.value%('insert payload'))

    return jsonBody

def getTableAndFields(record):
    try:
        table = record["table"]
    except KeyError:
        raise SkyflowError(SkyflowErrorCodes.INVALID_INPUT, SkyflowErrorMessages.TABLE_KEY_ERROR)
    
    try:
        fields = record["fields"]
    except KeyError:
        raise SkyflowError(SkyflowErrorCodes.INVALID_INPUT, SkyflowErrorMessages.FIELDS_KEY_ERROR)

    return (table, fields)

def processResponse(response: requests.Response, tokens: bool):
    # Todo: add tokens switch to code
    statusCode = response.status_code
    strcontent = response.content.decode('utf-8')
    try:
        response.raise_for_status()
        return strcontent
    except HTTPError:
        raise SkyflowError(statusCode, strcontent)

