from boto3 import client as boto3_client
import os

input_bucket = "cc-ss-input-3"
output_bucket = "cc-ss-output-3"
test_cases = "test_cases/"
rgw_endpoint = 'YOUR_CEPH_RGW_ENDPOINT_URL'
access_key = 'DCMF3Y05B3MFMB48SBQ4'
secret_key = 'wqX7S1GoxtwCoTXS4urCBABJ3WqvN2aQdWVNetTD'

def clear_input_bucket():
	global input_bucket
	s3 = boto3_client.client('s3',
					  endpoint_url=rgw_endpoint,
					  aws_access_key_id=access_key,
					  aws_secret_access_key=secret_key)
	list_obj = s3.list_objects_v2(Bucket=input_bucket)
	try:
		for item in list_obj["Contents"]:
			key = item["Key"]
			s3.delete_object(Bucket=input_bucket, Key=key)
	except:
		print("Nothing to clear in input bucket")
	
def clear_output_bucket():
	global output_bucket
	s3 = boto3_client.client('s3',
							 endpoint_url=rgw_endpoint,
							 aws_access_key_id=access_key,
							 aws_secret_access_key=secret_key)
	list_obj = s3.list_objects_v2(Bucket=output_bucket)
	try:
		for item in list_obj["Contents"]:
			key = item["Key"]
			s3.delete_object(Bucket=output_bucket, Key=key)
	except:
		print("Nothing to clear in output bucket")

def upload_to_input_bucket_s3(path, name):
	global input_bucket
	s3 = boto3_client('s3')
	s3.upload_file(path + name, input_bucket, name)
	
	
def upload_files(test_case):	
	global input_bucket
	global output_bucket
	global test_cases
	
	
	# Directory of test case
	test_dir = test_cases + test_case + "/"
	
	# Iterate over each video
	# Upload to S3 input bucket
	for filename in os.listdir(test_dir):
		if filename.endswith(".mp4") or filename.endswith(".MP4"):
			print("Uploading to input bucket..  name: " + str(filename)) 
			upload_to_input_bucket_s3(test_dir, filename)
			
	
def workload_generator():

	print("Running Test Case 1")
	upload_files("test_case_1")

	print("Running Test Case 2")
	upload_files("test_case_2")
	


if __name__ == '__main__':
	clear_input_bucket()
	clear_output_bucket()
	workload_generator()