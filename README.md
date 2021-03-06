# Serverless Computer Vision Pipeline
### [THIS TUTORIAL IS OUTDATED DUE TO RECENT AWS CHANGES]
Updated version [here](https://github.com/malcolmsfraser/AWS-ServerlessPipeline2)
#### Demo video
[![alt text](https://github.com/malcolmsfraser/Serverless-Pipeline/blob/main/Images/706Thumbnail.jpg)](https://youtu.be/5UWxFUAvRuQ)

## Introduction

This project demos how to create an infinitely scalable serverless data engineering pipeline. While this specific pipeline performs computer vision, the concepts shown can easily be extended to other tasks like natural language processing or involve the use of any other pretrained models.

The serverless pipeline listens to an S3 bucket for an image upload. Upon image upload the producer lamba function sends the name(s) of any uploaded file(s) to an SQS queue. The essentially infinite storage capacity of AWS S3 combined with the ability for AWS SQS to handle infinately large inputs is what allows this pipeline to scale from just a single upload to multiple files. Once in SQS, the labler lambda function in triggered which sends the files S3 location to AWS Rekognition which performs entity and text detection. The output response from Rekognition is then stored as a csv in the results folder of the same S3 bucket.

The included command-line tool allows you up upload a local file directly from your command-line and returns the computer vision results.

## Components

**IAM Role** that allows access to all services

**S3 bucket** which will store the target files and the results 

**Producer** lambda function that sends newly uploaded filenames to SQS

**Simple Queue Service (SQS)** queue which queues the files for processing

**Labeler** lambda function that calls AWS Rekognition on the queued files


## Design
![alt text](https://github.com/malcolmsfraser/Serverless-Pipeline/blob/main/Images/pipeline%20diagram.png)

## Setup
Follow these instructions to set up this pipeline on your own

### Create an IAM Role
Navigate to the IAM home page and select "Roles"

Create a new role for Lambda

On the permissions page select the following access policies:

![alt text](https://github.com/malcolmsfraser/Serverless-Pipeline/blob/main/Images/IamRoles.png)

Create role (remember the name for later)

### Create an SQS Queue
Navigate to the SQS home page and create a new queue

Name: producer

**Note: if you use another name you will need to update the name in the Producer lambda source code**

![alt text](https://github.com/malcolmsfraser/Serverless-Pipeline/blob/main/Images/UpdateProducer.png)
### Create an S3 Bucket
Navigate to the S3 home page and create a new bucket

Name: unprocessed-bucket

Region: us-east-1

**Note: if you use another name or region you will need to update the name in the Producer lambda & Labeler lambda source code**

![alt text](https://github.com/malcolmsfraser/Serverless-Pipeline/blob/main/Images/UpdateLabeler.png)
![alt text](https://github.com/malcolmsfraser/Serverless-Pipeline/blob/main/Images/UpdateProducer.png)

### Set up the serverless functions with AWS Lambda
#### Step 1: Create an AWS Cloud9 Environment
create and source a virtual environment
```{bash}
python3 -m venv ~/.pipeline
source ~/.pipeline/bin/activate
```
#### Step 2: Clone this repo
Clone repo and install dependencies
```{bash}
git clone https://github.com/malcolmsfraser/Serverless-Pipeline.git
cd Serverless-Pipeline
make install
```

#### Step 3: Producer Lambda
##### Initialize an new Lambda Function
![alt text](https://github.com/malcolmsfraser/Serverless-Pipeline/blob/main/Images/Lambda1.png)

Name your lambda whatever you want

Runtime: Python 3.6

Function Trigger: None

IAM Role: Select your created IAM Role

##### Copy contents from this repo's producer folder into your lambda folder
```{bash}
cd ~/environment
cp -r Serverless-Pipeline/producer/* {your-producer-name}/{your-producer-name}/
```
##### Install producer lambda dependencies
```{bash}
cd {your-producer-name}/{your-producer-name}
make all
```

#### Step 4: Labeler Lambda
##### Initialize an new Lambda Function
Name your lambda whatever you want

Runtime: Python 3.6

Function Trigger: None

IAM Role: Select your created IAM Role

##### Copy contents from this repo's labeler folder into your lambda folder
```{bash}
cd ~/environment
cp -r Serverless-Pipeline/labeler/* {your-labeber-name}/{your-labeber-name}/
```
##### Install labeler lambda dependencies
```{bash}
cd {your-labeler-name}/{your-labeler-name}
make all
```
#### Step 5: Deploying & Trigger Setup
Deploy your lambda functions from AWS Cloud9
![alt text](https://github.com/malcolmsfraser/Serverless-Pipeline/blob/main/Images/LambdaDeploy.png)

From the AWS Lambda console, select the appropriate lambda function and setup triggers
![alt text](https://github.com/malcolmsfraser/Serverless-Pipeline/blob/main/Images/Lambda2.png)

#### For the producer lambda setup an S3 trigger
Trigger should be listening to the S3 bucket you created earlier

![alt text](https://github.com/malcolmsfraser/Serverless-Pipeline/blob/main/Images/lambdaProdTrigger.png)

#### For the labeler lambda setup an SQS trigger
Trigger should be listening to the SQS queue you created earlier

![alt text](https://github.com/malcolmsfraser/Serverless-Pipeline/blob/main/Images/lambdaLabTrigger.png)

The pipeline setup is now complete!

## Using the command-line interface
To use the command line tool copy the file from this repo into your Cloud9 main environment
```{bash}
cd ~/environment/Serverless-Pipeline
cp visionCLI.py ..
```

Test with any image file (I've provided one called billboard.jpg)
```{bash}
cd ~/environment
python visionCLI --file billboard.jpg --bucket unprocessed-bucket
```

