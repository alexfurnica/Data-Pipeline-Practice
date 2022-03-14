import boto3
import json
import time
import pandas as pd
import utils

# SQS client library
sqs = boto3.client(
    'sqs',
    endpoint_url='http://localhost:4572', #only for test purposes
    use_ssl=False, # only for test purposes
    region_name='us-east-1'
)

queue_url = 'http://localhost:4572/123456789012/sse_queue'

s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:4572', #only for test purposes
    use_ssl=False, # only for test purposes
    region_name='us-east-1'
)

# desired payload
MAP_KEYS = ['id', 'type', 'namespace', 'title', 'comment', 'timesamp', 'user', 'bot', 'ReceiptHandle']
list_msgs = []

def read_batch():
    '''Reads in, processes, and sends to S3 messages from the queue'''

    while True:
        try:
            response = sqs.receive_message(
                QueueUrl = queue_url,
                MaxNumberOfMessages = 10 # Max batch size
            )
            process_batch(response['Messages'])
        except KeyError:
            print('\rNo messages available, retrying in 5 seconds...', sep=' ', end='', flush=True)
            time.sleep(5)

def process_batch(messages: dict):
    '''Cleans incoming messages and sends batches to S3

    Only keeps the data in the body of the message under the keys defined by
    the MAP_KEYS list. Once at least 100 messages have been collected, they
    are sent to the defined S3 bucket.
    '''

    global list_msgs
    print('\rProcessing messages...', flush=True, end='')
    for message in messages:
        d = json.loads(message['Body'])

        # Clean the message body from non-desired data
        clean_dict = {key:(d[key] if key in d else None) for key in MAP_KEYS}

        # Enrich df with the message's receipt handle in order to clean it from the queue
        clean_dict['ReceiptHandle'] = message['ReceiptHandle']
        list_msgs.append(clean_dict)

    if len(list_msgs) >= 100:
        print('\rBatch ready to be exported to the Data Lake', sep=' ', end='', flush=True)
        to_data_lake(list_msgs)
        list_msgs = list()

def to_data_lake(df: pd.DataFrame):
    '''Sends a batch of data to the data lake (S3)'''

    batch_df = pd.DataFrame(list_msgs)
    csv = batch_df.to_csv(index=False)
    filename = f'batch-{df[0]["id"]}.csv'

    #csv to s3 bucket
    s3.put_object(Bucket='sse-bucket', Key=filename, Body=csv, ACL='public-read')
    print(f'\r{filename} saved into the Data Lake', sep=' ', end='', flush=True)
    remove_messages(batch_df)

def remove_messages(df: pd.DataFrame):
    '''Removes messages that were processed from the SQS queue
    '''
    for receipt_handle in df['ReceiptHandle'].values:
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
    
if __name__ == '__main__':
    utils.clear_console()
    read_batch()