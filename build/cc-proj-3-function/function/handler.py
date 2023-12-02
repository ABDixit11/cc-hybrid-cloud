import face_recognition
import pickle
import os
import subprocess
import boto3
import logging
import csv
import sys
import json
from io import StringIO

# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOGLEVEL", "INFO"))
logger.setLevel(logging.INFO)

aws_access_key = 'AKIA4BR5QBAMM5BKK5Q5'
aws_secret_key = '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'

ceph_access_key = 'fooAccessKey'
ceph_secret_key = 'fooSecretKey'
input_bucket = "cc-ss-input-3"
output_bucket = "cc-ss-output-3"
rgw_endpoint = 'http://10.0.2.15:7480'

# Initialize S3 client

file_path = '/home/app/function/encoding'
table_name = 'cc-ss-proj2-table'

ceph_s3 = boto3.client('s3',
                       endpoint_url=rgw_endpoint,
                       aws_access_key_id=ceph_access_key,
                       aws_secret_access_key=ceph_secret_key)


# Function to read the 'encoding' file
def open_encoding(filename):
    with open(filename, "rb") as file:
        data = pickle.load(file)
    return data


def get_info_from_dynamo(name):
    dynamodb = boto3.client('dynamodb',
                            aws_access_key_id=aws_access_key,
                            aws_secret_access_key=aws_secret_key,
                            region_name='us-east-1')
    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key={
                'name': {'S': name}
            }
        )
        if 'Item' in response:
            item = response['Item']
            return item
        else:
            return "Item not found in DynamoDB."
    except Exception as e:
        return str(e)


def convert_ddb_item_to_row(fieldnames, information_from_dynamo):
    row = {}
    for key in fieldnames:
        value = information_from_dynamo[key]['S']
        logger.info(type(value))
        row[key] = str(value)
    return row


def upload_file_to_s3(video_file_name, information_from_dynamo):
    global  ceph_s3
    bucket_name = 'cc-ss-output-3'
    object_name = video_file_name.replace('.mp4', '') + ".csv"
    csv_data = StringIO()
    fieldnames = ['name', 'major', 'year']
    row = convert_ddb_item_to_row(fieldnames, information_from_dynamo)
    csv_writer = csv.DictWriter(csv_data, fieldnames=fieldnames)
    csv_writer.writeheader()
    csv_writer.writerow({'name': row['name'], 'major': row['major'], 'year': row['year']})

    ceph_s3.put_object(Bucket=bucket_name, Key=object_name, Body=csv_data.getvalue())


def compare_encoding(array, arrays):
    for i in range(len(arrays)):
        result = face_recognition.compare_faces(array, arrays[i])
        if all(result):
            return i
    return -1


def handle(event):
    try:
        s3_event=event
        if not isinstance(event,dict):
            s3_event= json.loads(event)
        global ceph_s3
        encoding_dict = open_encoding(file_path)
        encoding_names = encoding_dict['name']
        encoding_values = encoding_dict['encoding']
        key = "placeholder"
        for record in s3_event['Records']:
            print("hello")
            print(record)
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            frame_dir = "/home/app/function/tmp/frames/"
            os.makedirs(frame_dir, exist_ok=True)
            video_path = "/home/app/function/tmp/" + key
            video_dir = '/'.join(video_path.split('/')[:-1])
            os.makedirs(video_dir, exist_ok=True)
            ceph_s3.download_file(bucket, key, video_path)
            frame_pattern = f"{frame_dir}%04d.jpg"
            subprocess.call(['ffmpeg', '-i', video_path, frame_pattern])
            frame_files = os.listdir(frame_dir)
            frame_files.sort()
            result = None
            for frame_file in frame_files:
                frame_image = face_recognition.load_image_file(os.path.join(frame_dir, frame_file))
                unknown_face_encoding = face_recognition.face_encodings(frame_image)
                result = compare_encoding(unknown_face_encoding, encoding_values)
                if result != -1:
                    break
            if result != -1:
                name_of_person_detected = encoding_names[result]
                logger.info(
                    f"First face detected for {key}! Name of the person identified is: {name_of_person_detected}")
                info_from_ddb = get_info_from_dynamo(name_of_person_detected)
                logger.info(info_from_ddb)
                upload_file_to_s3(key, info_from_ddb)
            else:
                logger.info(f"No faces detected for: {key}")
            for frame_file in frame_files:
                os.remove(os.path.join(frame_dir, frame_file))
            os.remove(video_path)
        return {
            'statusCode': 200,
            'body': f'Processing complete. File Uploaded to S3 for video: {key}'
        }
    except Exception as e:
        raise e
