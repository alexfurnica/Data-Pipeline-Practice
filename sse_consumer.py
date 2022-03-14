import boto3
import json
from sseclient import SSEClient as EventSource

# SQS client library
sqs = boto3.client(
    'sqs',
    endpoint_url='http://localhost:4572', # only for test purposes
    use_ssl=False, # only for test pusposes
    region_name='us-east-1'
)

queue_url = 'http://localhost:4572/123456789012/sse_queue'

def catch_events():
    url = 'https://stream.wikimedia.org/v2/stream/recentchange'
    for event in EventSource(url):
        if event.event == 'message':
            try:
                message = json.loads(event.data)
            except ValueError:
                pass
            else:
                enqueue_message(json.dumps(message))

def enqueue_message(message):
    response = sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=1,
        MessageBody=message
    )

    print(f'\rMessage {response["MessageId"]} enqueued', sep=' ', end='', flush=True)

if __name__ == '__main__':
    catch_events()