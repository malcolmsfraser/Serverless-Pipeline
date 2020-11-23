# Serverless Computer Vision Pipeline

## Introduction

This project outlines all the copunents needed to create an infinitely scalable serverless data engineering pipeline. While this specific example performs computer vision, the concepts shown can easily be extended to other tasks like natural language processing or involve the use of any other pretrained models.

The serverless pipeline listens to an S3 bucket for an image upload. Upon image upload the producer lamba function sends the name(s) of any uploaded file(s) to an SQS queue. The essentially infinite storage capacity of AWS S3 combined with the ability for AWS SQS to handle infinately large inputs is what allows this pipeline to scale from just a single upload to multiple files. Once in SQS, the labler lambda function in triggered which sends the files S3 location to AWS Rekognition which performs entity and text detection. The output response from Rekognition is then stored as a csv in the results folder of the same S3 bucket.

## Components

IAM Role that allows access to all services
S3 bucket which will store the target files and the results 
Producer lambda function that sends newly uploaded filenames to SQS
Simple Queue Service (SQS) queue which queues the files for processing
Labeler lambda function that calls AWS Rekognition on the queued files


## Design
![alt text](https://github.com/malcolmsfraser/Serverless-Pipeline/blob/main/pipeline%20diagram.png)

## Setup

### Create an IAM Role


### Setting up the serverless functions with AWS Lambda

#### Step 1: Create an AWS Cloud9 Environment

#### Step 2: Producer Lambda Initialize an new Lambda Function
Name your lambda whatever you want
Runtime: Python 3.6
Function Trigger: None
IAM Role: Select your created IAM Role
