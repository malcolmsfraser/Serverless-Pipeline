import click
import pandas as pd
import boto3
import time
from tqdm import tqdm

def s3_client_connection():
    c = boto3.client('s3')
    return c


def send_to_s3(file,bucket):
    """Sends file to s3 bucket"""
    
    client = s3_client_connection()
    
    print(f"Uploading file: {file} to bucket: {bucket}.")
    response = client.put_object(
        Body=file,
        Bucket=bucket,
        Key=file,
        )
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
    for i in tqdm(range(10)):
        time.sleep(.7)
    info = get_results(file,bucket)
    print(f"Filename:\n{info['Image'][0]}:\n\nLabels detected:\n{info['Labels'][0]}\n\nText Detected:\n{info['Text'][0]}")


if __name__ == "__main__":
    # pylint --disable=no-value-for-parameter
    cool_stuff()
    


