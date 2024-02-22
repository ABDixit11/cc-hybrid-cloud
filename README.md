#  Serverless server Cloud computing project 3: Smart Classroom Assistant using Hybrid Cloud

## Group Members: (Team Name : Serverless server)
    1. Bhavesh khubnani
    2. Aishwariya Ranjan
    3. Abhijeet Dixit

## AWS Credentials :
    Configure your secret key and access key

## S3 Buckets : 
    1. Input bucket  : cc-ss-input-3
    2. Output Bucket : cc-ss-output-3

## Steps to run the code from scratch :

    1. Clone the Repository
        Clone this repository to your local machine.

    2. Create a Linux-based Virtual Machine (Pre-requisite :  You should download an image of the OS that you want to install for.eg. Ubuntu 22.x and also install VirtualBox/VMware)

    3. Install Docker
    
    4. Follow the instructions to set up OpenFaaS using arkade and kinD (https://docs.openfaas.com/tutorials/local-kind-registry/)
	
    5. Follow the tutorial to setup CEPH cluster on sigle node (https://canonical-microceph.readthedocs-hosted.com/en/latest/tutorial/single-node/)

    6. Enable the RGW service (https://canonical-microceph.readthedocs-hosted.com/en/latest/how-to/enable-service-instances/)

    7. Log in to the CEPH dashboard and create buckets and user with S3 keys.

    8. Create a DynamoDB table with 'name' as the primary key. This table will be used to store information related to recognized faces.
    
    9. Add the secret key and access key of S3 and the CEPH user to the handler.py file so that OpenFaaS can connect to the DynamoDB instance as well as the CEPH cluster.

    10. Use the build and deploy command to push the code and deploy the OpenFaaS function. (https://docs.openfaas.com/tutorials/local-kind-registry/#build-push-deploy)

    11. Run the workload.py script to upload two batches of test videos : 9 videos and 100 videos.
    
    12. Monitor the Output Bucket to access details of recognized faces in the uploaded videos.
