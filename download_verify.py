from boto3 import client as boto3_client
import os

input_bucket = "cc-ss-input-3"
output_bucket = "cc-ss-output-3"
test_cases = "test_cases/"
rgw_endpoint = 'http://10.0.2.15:7480'
access_key = 'fooAccessKey'
secret_key = 'fooSecretKey'
ceph_s3 = boto3_client('s3',
                       endpoint_url=rgw_endpoint,
                       aws_access_key_id=access_key,
                       aws_secret_access_key=secret_key)


def download_a_file():
    global ceph_s3
    key=""
    list_obj = ceph_s3.list_objects_v2(Bucket='cc-ss-output-3')
    key=list_obj['Contents'][0]['Key']
    ceph_s3.download_file('cc-ss-output-3', key, "/home/bhavesh/outputs/" + key)


if __name__ == '__main__':
    download_a_file()
