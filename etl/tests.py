
import unittest
from django.test import TestCase, Client
import os
import boto3
from simetric.settings import S3_BUCKET
from simetric.helpers.database import create_conn
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import inspect
import time
# Create your tests here.

class SimpleTest(unittest.TestCase):
    def test_upload(self):
        c = Client()
        fpath = os.environ['PWD'] + '/example/titanic.csv'
        with open(fpath) as fp:
            response = c.post('/etl/', {'title': 'titanic', 'file': fp})
        self.assertEqual(response.status_code, 200)
        time.sleep(30)

        s3client = boto3.client('s3')
        response = s3client.list_objects(
            Bucket=S3_BUCKET,
            Delimiter=',',
            EncodingType='url',
            Prefix='uploads/titanic.csv',
            RequestPayer='requester'
        )
        self.assertEqual(len(response['Contents']), 1)

        conn = create_conn()
        inspector = inspect(conn)
        r = inspector.get_columns('titanic')
        self.assertEqual(len(r) > 0, True)
