# -*- coding: utf-8 -*-
import boto3, xlrd, uuid, json

s3 = boto3.resource('s3')
url_payload = { "freshen_url": "https://api.trade.gov/v1/steel_data/freshen.json?api_key="}
lambda_client = boto3.client('lambda')

def handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    bucket = s3.Bucket(bucket_name)

    data = []
    headers = []

    for obj in bucket.objects.all():
      path = obj.key
      download_path = '/tmp/{}{}'.format(uuid.uuid4(), path)
      bucket.download_file(path, download_path)

      book = xlrd.open_workbook(download_path)
      sheet = book.sheets()[0]

      if not headers:
        headers = map(get_value, sheet.row(0))

      for i in range(1, sheet.nrows):
        data.append(map(get_value, sheet.row(i)))

    data.insert(0, headers)
    upload_csv_file(data)


def upload_csv_file(data):
  csv_rows = [",".join(row) for row in data]
  csv_string = "\n".join(csv_rows)
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

def get_value(cell):
  return str(cell.value)