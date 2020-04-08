# -*- coding: utf-8 -*-
import csv
import json
import uuid
from collections import OrderedDict

import boto3

URL_PAYLOAD = {
    "freshen_url": "https://api.trade.gov/v1/steel_data_staging/freshen?api_key="
}


def handler(event, context):
    s3 = boto3.resource("s3")
    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    bucket = s3.Bucket(bucket_name)

    data = []
    global_headers = []
    outcome = True
    for obj in bucket.objects.all():
        path = obj.key
        download_path = "/tmp/{}{}".format(uuid.uuid4(), path)
        print(download_path)
        bucket.download_file(path, download_path)
        with open(download_path) as csvfile:
            reader = csv.reader(csvfile)
            header = [x.lower() for x in next(reader, None)]
            global_headers = list(set(global_headers + header))
            for row in reader:
                data.append(dict(zip(header, map(get_value, row))))

    empty_entry = build_empty_entry(global_headers)
    # Expand entries to include all headers
    data = map(lambda x: OrderedDict(empty_entry, **x), data)
    csv_string = build_csv_string(data)
    if upload_csv_file(s3, csv_string):
        lambda_client = boto3.client("lambda", region_name="us-east-1")
        lambda_client.invoke(
            FunctionName="endpoint_freshen",
            InvocationType="Event",
            Payload=json.dumps(URL_PAYLOAD),
        )
        print("Freshening data...")
    else:
        print("Error writing file to S3 bucket")
        outcome = False
    return outcome


def get_value(entry):
    if "," in entry:
        entry = '"' + entry + '"'
    return entry


def upload_csv_file(s3, csv_string):
    response = s3.Object("steel-data-csv", "entries-staging.csv").put(
        Body=csv_string, ContentType="application/csv", ACL="public-read"
    )
    return response["ResponseMetadata"]["HTTPStatusCode"] == 200


def build_empty_entry(global_headers):
    global_headers.sort()
    # updated_date as the last element in the header list
    global_headers.insert(len(global_headers) - 1, global_headers.pop(5))
    empty_entry = OrderedDict()
    for header in global_headers:
        empty_entry[header] = ""
    return empty_entry


def build_csv_string(data):
    first_row = next(data)
    csv_string = ",".join(first_row.keys()) + "\n"
    csv_string += ",".join(first_row.values()) + "\n"

    for entry in data:
        csv_string += ",".join(entry.values()) + "\n"

    return csv_string
