import click
import pandas as pd
import boto3
import time
from tqdm import tqdm

def s3_client_connection():
    c = boto3.client('s3')
    return c
    
def s3_resource_connection():
    r = boto3.resource('s3')
    return r


def send_to_s3(file,bucket):
    """Sends file to s3 bucket"""
    
    
    print(f"Uploading file: {file} to bucket: {bucket}.")
    s3 = s3_resource_connection()
    s3.meta.client.upload_file(file, bucket, file)
    print("Upload complete.")
    return None

def get_results(file,bucket):
    """Retrieves computer vision results"""
    
    fname = f"labels/['{file[:-4]}']_labels.csv"
    client = s3_client_connection()
    response = client.get_object(
        Bucket=bucket,
        Key=fname
        )
    df = pd.read_csv(response["Body"])
    if "Unnamed: 0" in df.columns:
        df.drop("Unnamed: 0", axis=1, inplace=True)
    info = df.to_dict()
    return info

@click.command()
@click.option("--file", help = 'Name of image file')
@click.option('--bucket', help = 'Name of s3 bucket')
def cool_stuff(file, bucket):
    send_to_s3(file,bucket)
    print('Analyzing image')
    for i in tqdm(range(12)):
        time.sleep(i+1-i)
    info = get_results(file,bucket)
    print(f"Filename:\n{info['Image'][0]}\n\nLabels detected:\n{info['Labels'][0]}\n\nText Detected:\n{info['Text'][0]}")


if __name__ == "__main__":
    # pylint --disable=no-value-for-parameter
    cool_stuff()
    


