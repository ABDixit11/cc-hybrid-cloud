import time
import json
from boto3 import client as boto3_client
import requests

# Ceph RGW S3 configurations
ceph_rgw_endpoint  = 'http://10.0.2.15:7480'
ceph_rgw_access_key_id = 'fooAccessKey'
ceph_rgw_secret_access_key = 'fooSecretKey'
bucket_name = 'cc-ss-input-3'

# OpenFaaS function URL
openfaas_url = 'http://127.0.0.1:8080/function/cc-proj-3-function'

# Set up S3 client with Ceph RGW configurations
s3_client = boto3_client('s3', endpoint_url=ceph_rgw_endpoint, aws_access_key_id=ceph_rgw_access_key_id,
                         aws_secret_access_key=ceph_rgw_secret_access_key)

def list_objects(bucket_name):
    global s3_client
    list_obj = s3_client.list_objects_v2(Bucket=bucket_name)
    # List objects in the bucket
    print(list_obj)
    return list_obj.get('Contents', [])


def forward_to_openfaas(event_data):
    # Convert event data to a string
    event_data_str = json.dumps(event_data)
    # Forward the event data as text to the OpenFaaS function
    headers = {'Content-Type': 'text/plain'}
    response = requests.post(openfaas_url, data=event_data_str, headers=headers)
    return response.status_code


def monitor_s3_bucket(bucket_name):
    while True:
        print("Listening for newly created objects in cc-ss-input-3")
        # Get the list of objects in the bucket
        objects = list_objects(bucket_name)
        if objects!=[]:
            print("Found new objects")

        for obj in objects:
            # Assuming you want to consider only newly created objects
            if obj['Key'] not in processed_objects:
                event_data = {
                    'Records': [
                        {'s3':
                            {'bucket': {
                                'name': bucket_name
                            },
                                'object': {
                                    'key': obj['Key']
                                }
                            }}]}

                # Forward the event data as text to the OpenFaaS function
                status_code = forward_to_openfaas(event_data)
                print(f"Event forwarded to OpenFaaS with status code {status_code}")

                # Add the processed object to the list
                processed_objects.add(obj['Key'])



if __name__ == '__main__':
    processed_objects = set()  # Set to keep track of processed objects
    monitor_s3_bucket(bucket_name)
