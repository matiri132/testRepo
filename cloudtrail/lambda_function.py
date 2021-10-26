from __future__ import print_function
import os
import boto3
import json
import datetime
import gzip
import urllib
import urllib3
import logging
import requests
import tempfile
from io import BytesIO
from pprint import pprint
from requests_aws4auth import AWS4Auth



"""
Can override the global variables using Lambda Environment Parameters
"""
globalVars = {}
globalVars['awsRegion'] = os.environ.get('AWS_REGION' , 'us-east-1')
globalVars['esHosts'] = os.environ.get('OPENSEARCH_ENDPOINT' , '')
globalVars['service'] = "es"
globalVars['esIndexPrefix'] = "cloudtrail-"
globalVars['esIndexDocType'] = "_doc"


# Initialize Logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def indexDocElement(es_Url, awsauth, data):
    try:
        headers = {"Content-Type": "application/json"}
        resp = requests.post(es_Url, auth=awsauth,
                             headers=headers, data=data)
        if resp.status_code == 201:
            logger.info('INFO: Successfully inserted element into ES')
        else:
            logger.error('FAILURE: Unable to index element')
    except Exception as e:
        logger.error('ERROR: {0}'.format(str(e)))
        print(e)


def lambda_handler(event, context):
    s3 = boto3.client('s3')
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key,
                       credentials.secret_key,
                       globalVars['awsRegion'],
                       globalVars['service'],
                       session_token=credentials.token
                       )

    logger.info("Received event: " + json.dumps(event, indent=2))

    bucket = event['Records'][0]['s3']['bucket']['name']
    print('Bucket:' + bucket)
    key = urllib.parse.unquote_plus(
        event['Records'][0]['s3']['object']['key'])
    print('Key:' + str(key))
    # Get document (obj) from S3
    s3obj = tempfile.NamedTemporaryFile(mode='w+b', delete=False)
    s3.download_fileobj(bucket, key, s3obj)
    gzfile = gzip.open(s3obj.name, "r")
    lines = json.loads(gzfile.readlines()[0])

    logger.info('SUCCESS: Retreived object from S3')

    eventcount = 1
    for i in lines["Records"]:
        i.pop('apiVersion', None)
        i["eventSource"] = i["eventSource"].split(".")[0]
        data = json.dumps(i).encode('utf-8')

        # Index each line into ES Domain
        date = datetime.datetime.now().strftime("%Y.%m.%d")
        indexName = globalVars['esIndexPrefix'] + date
        es_Url = globalVars['esHosts'] + '/' + \
            indexName + '/' + globalVars['esIndexDocType']

        indexDocElement(es_Url, awsauth, data)

        eventcount += 1

    s3obj.close()
    os.unlink(s3obj.name)
    print("{} events in {}".format(eventcount, s3obj.name))


if __name__ == '__main__':
    lambda_handler(None, None)
