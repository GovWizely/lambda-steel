# -*- coding: utf-8 -*-
import boto3, xlrd, uuid, json
from collections import OrderedDict

s3 = boto3.resource('s3')
url_payload = { "freshen_url": "https://api.trade.gov/v1/steel_data/freshen.json?api_key="}
lambda_client = boto3.client('lambda')

def handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    bucket = s3.Bucket(bucket_name)

    data = []
    headers = []
    global_headers = []
    for obj in bucket.objects.all():
      path = obj.key
      download_path = '/tmp/{}{}'.format(uuid.uuid4(), path)
      bucket.download_file(path, download_path)
      book = xlrd.open_workbook(download_path)
      sheet = book.sheets()[0]

      headers = map(get_header, sheet.row(0))
      global_headers = list(set(global_headers + headers))

      for i in range(1, sheet.nrows):
        data.append(dict(zip(headers, map(get_value, sheet.row(i)))))

    empty_entry = build_empty_entry(global_headers)
    data = map(lambda x: OrderedDict(empty_entry, **x), data)  # Expand entries to include all headers
    csv_string = build_csv_string(data)
  
    upload_csv_file(csv_string)

def upload_csv_file(csv_string):
  try:
    response = s3.Object('steel-data-csv', 'entries.csv').put(Body=csv_string, ContentType='application/csv', ACL='public-read')
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
      lambda_client.invoke(FunctionName="endpoint_freshen", InvocationType='Event', Payload=json.dumps(url_payload))
      print("Freshening data...")
    return response
  except Exception as e:
    print("Error writing file to S3 bucket: ")
    print(e)
    raise e

def get_header(cell):
  return str(cell.value).lower()

def get_value(cell):
  return str(cell.value)

def build_empty_entry(global_headers):
  global_headers.sort()
  empty_entry = OrderedDict()
  for header in global_headers:
    empty_entry[header] = ""
  return empty_entry

def build_csv_string(data):
  csv_string = ",".join(data[0].keys()) + '\n'

  for entry in data:
    csv_string += ",".join(entry.values())
    csv_string += '\n'
  return csv_string
