import json
import os

import boto3
import pytest
from moto import mock_lambda, mock_s3

from service import handler


@pytest.fixture
def event():
    with open("event.json") as f:
        event = json.load(f)
    return event


def return_event():
    import zipfile
    import io

    code = """def lambda_handler(event, context):\n   return True"""
    zip_output = io.BytesIO()
    zip_file = zipfile.ZipFile(zip_output, 'w', zipfile.ZIP_DEFLATED)
    zip_file.writestr('service.py', code)
    zip_file.close()
    zip_output.seek(0)
    return zip_output.read()


@mock_s3
@mock_lambda
def test_handler(event):
    """Reads several files from S3, processes them into a single CSV file, uploads that to
    another S3 bucket, and invokes the lambda.
    """
    conn = boto3.resource("s3")
    # We need to create the buckets and the lambda since this is all in Moto's 'virtual' AWS account
    conn.create_bucket(Bucket="steel-data-raw")
    conn.create_bucket(Bucket="steel-data-csv")
    lambda_client = boto3.client("lambda", region_name="us-east-1")
    lambda_client.create_function(
        FunctionName="endpoint_freshen",
        Runtime='python3.8',
        Role='lambda_api',
        Handler='service.handler',
        Code={
            'ZipFile': return_event(),
        },
        Publish=True,
        Timeout=30,
        MemorySize=128
    )
    # Put some fixture files into the raw bucket
    for entry in os.scandir("fixtures"):
        with open(entry) as fp:
            conn.Object("steel-data-raw", entry.name).put(
                Body=fp.read(), ContentType="application/csv", ACL="public-read"
            )

    assert handler(event, None) is True
    body = (
        conn.Object("steel-data-csv", "entries-staging.csv")
            .get()["Body"]
            .read()
            .decode("utf-8")
    )
    expected_line_count = 1054
    expected_headers = (
        "flow_type,partner,product,reporter,trade,y_2012_ihs,y_2013_ihs,"
        "y_2014_ihs,y_2015_ihs,y_2016_ihs,y_2017_ihs,y_2018_ihs,y_2019_ihs,ytd,"
        "ytd_2018,ytd_2019,ytd_2020,updated_date"
    )
    expected_first_line = (
        "QTY,United Arab Emirates,All Steel Mill Products,Iran,EXP,207023.52,"
        "221079.406,469752.2,580709.15,917373.044,1416833.674,1436982.858,,Apr,"
        "631670.844,53058.385,,03JUN2019"
    )
    csv_array = body.split("\n")

    assert len(csv_array) == expected_line_count
    assert csv_array[0] == expected_headers
    assert csv_array[1] == expected_first_line
