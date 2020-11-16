import boto3
import botocore
import pandas as pd
import json
from io import StringIO


# SETUP LOGGING
import logging
from pythonjsonlogger import jsonlogger

LOG = logging.getLogger()
LOG.setLevel (logging.INFO)
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
LOG.addHandler(logHandler)

REGION = 'us-east-1'
BUCKET = 'unprocessed-bucket'

def sqs_queue_resource(queue_name):
	"""
	Returns an SQS queue resource connection
	"""
	
	sqs_resource = boto3.resource('sqs', region_name=REGION)
	log_sqs_resource_msg = "Creating SQS resource conn with qname: [%s] in region: [%s]" % (queue_name, REGION)
	LOG.info(log_sqs_resource_msg)
	queue = sqs_resource.get_queue_by_name(QueueName=queue_name)
	return queue
   
	
def sqs_connection():
	"""
	Creatd an SQS Connection which defaults to global var REGION
	"""
	
	sqs_client = boto3.client('sqs', region_name = REGION)
	log_sqs_client_msg = "Creating SQS connection in Region: [%s]" % REGION
	LOG.info(log_sqs_client_msg)
	return sqs_client
	
def delete_sqs_msg(queue_name, receipt_handle):
	"""
	Deletes message from SQS queue.
	Returns a response
	"""
	
	sqs_client = sqs_connection()
	try:
		queue_url = sqs_client.get_queue_url(QueueName=queue_name)['QueueUrl']
		delete_log_msg = "Deleting msg with ReceiptHandle %s" % receipt_handle
		LOG.info(delete_log_msg)
		response = sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
	except botocore.exceptions.ClientError as error:
		exception_msg = "FAILURE TO DELETE SQS MSG: Queue Name [%s] with error [%s]" % (queue_name, error)
		LOG.exception(exception_msg)
		return None
		
	
	delete_log_msg_resp = 'Response from delete from queue: %s' % response
	LOG.info(delete_log_msg_resp)
	return response
	
def create_dataframe(image_names):
	"""
	Takes a list of image names
	Generates a dataframe with image name and detected labels
	"""
	
	LOG.info('Generating image name column')
	df = pd.DataFrame({'Image':image_names})
	return df


def generate_labels(image_name, bucket = BUCKET):
	
	LOG.info('Creating Rekognition Client')
	rekognition = boto3.client('rekognition')
	LOG.info(f'Generating labels for {image_name}')
	response = rekognition.detect_labels(
	Image={
		'S3Object': {
			'Bucket': bucket,
			'Name': image_name,
		}
	},
	MaxLabels=5,
)
	labels = ", ".join([label['Name'] for label in response['Labels']])
	LOG.info(f'Labels generates for image: {image_name}')
	return labels
	
def detect_text(image_name, bucket = BUCKET):
	
	LOG.info('Creating Rekognition Client')
	rekognition = boto3.client('rekognition')
	LOG.info(f'Detecting text for {image_name}')
	response = rekognition.detect_text(
		Image={
			'S3Object': {
				'Bucket': bucket,
				'Name': image_name,
			}
		}
	)
	text = " | ".join([item['DetectedText'] for item in response['TextDetections']])
	LOG.info(f'Text detected for image:{image_name}')
	return text

def apply_computer_vision(df,columns = 'Image'):
	
	df['Labels'] = df[columns].apply(generate_labels)
	df['Text'] = df[columns].apply(detect_text)
	return df

def delete_unprocessed(bucket, image_names):
	
	for image_name in image_names:
		s3_resource = boto3.resource('s3')
		LOG.info(f'Deleting image {image_name} from unprocessed folder')
		response = s3_resource.Object(bucket, image_name).delete()
		LOG.info(f'Image {image_name} deleted')
		return None
	
def copy_processed(bucket, image_names):
	
	for image_name in image_names:
		s3_resource = boto3.resource('s3')
		LOG.info(f'Moving image {image_name} to processed folder')
		response = s3_resource.Object(bucket, f'processed/{image_name}').copy_from(CopySource=f'unprocessed-bucket/{image_name}')
		LOG.info(f'Image {image_name} copied')
		return None

def write_s3(df, bucket, image_names):
	"""
	Write S3 Bucket
	"""
	names = [x[:-4] for x in image_names]
	
	csv_buffer = StringIO()
	df.to_csv(csv_buffer)
	s3_resource = boto3.resource('s3')
	filename = f"{names}_labels.csv"
	response = s3_resource.Object(bucket, f'labels/{filename}').put(Body=csv_buffer.getvalue())
	copy_processed(bucket, image_names)
	delete_unprocessed(bucket, image_names)
	LOG.info(f'Result of write to "processed" folder in bucket: {bucket} with:\n {response}')	
	

def lambda_handler(event, context):
	"""
	Lambda Entrypoint
	"""
	LOG.info(f'SURVEYJOB LAMBDA, event {event}, context {context}')
	receipt_handle = event['Records'][0]['receiptHandle']
	event_source_arn = event['Records'][0]['eventSourceARN']
	
	image_names = []
	
	# Process Queue
	for record in event['Records']:
		"""
		Generate list of images
		Delete queue messages
		"""
		image = json.loads(record['body'])

		# Capture for processing
		image_names.append(image)
		
		extra_logging = {"image":image}
		LOG.info(f"SQS CONSUMER LAMBDA, splitting sqs arn with value: {event_source_arn}",extra=extra_logging)
		qname = event_source_arn.split(':')[-1]
		extra_logging['qname'] = qname
		LOG.info(f"Attemping Deleting SQS receiptHandle {receipt_handle} with queue_name {qname}", extra=extra_logging)
		response = delete_sqs_msg(queue_name=qname, receipt_handle=receipt_handle)
		LOG.info(f"Deleted SQS receipt_handle {receipt_handle} with response {response}", extra=extra_logging)
		
	# Make dataframe with wikipedia summary snips
	LOG.info(f'Creating dataframe with values: {image_names}')
	df = create_dataframe(image_names)
	
	# Perform Sentiment Analysis
	df = apply_computer_vision(df)
	LOG.info(f'Computer vision stage complete: {df.to_dict()}')
	
	# Write result to S3
	write_s3(df=df, bucket=BUCKET, image_names=image_names)