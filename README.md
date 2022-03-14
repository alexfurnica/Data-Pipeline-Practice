# Streaming Data Pipeline Example

These scripts follow the tutorial found [here](https://www.activestate.com/blog/how-to-create-scalable-data-pipelines-with-python/). The main goal is to practice creating a scalable data pipeline to be fed into (cloud) analytics applications.

The Git repo for the original tutorial project is found [here](https://github.com/nickmancol/python_data_pipeline).

**Caution!**

Although the original article was updated in March 2021 (at current time of writing of this README), the scripts did not work out of the box and required some changes. Mainly:

* Use `moto_server` instead of e.g. `moto_server s3` &rarr; Using a specific `moto_server` instance per service did not work for me. I could not diagnose the exact issue, but using one generic `moto_server` instance worked in the end.
* `s3.Bucket().put_object()` needs to be replaced with `s3.put_object(Bucket=str)` &rarr; It's possible that the original tutorial mixed up the *client* interface with the *resource* interface.

## Requirements

This tool was developed and tested on Python 3.9.7. It is recommended that the same version of Python be installed for the tool to work.

Additionally, all package requirements can be installed by using the provided `requirements.txt` file:

```
> pip install -r requirements.txt
```

## How to use

Start a `moto_server` in order to create the mocked AWS services. Specifically, this tool makes use of S3 (for object storage) and SQS (for a message queueing service). To start the server on port 4572, run:

```
> moto_server -p 4572 -H localhost
```

Before running the tool, the mocked AWS services need to be instantiated on the `moto_server`. Start a separate terminal and type the following commands to start an SQS and S3 instance:

```
> aws --endpoint-url=http://localhost:4572 sqs create-queue --queue-name sse_queue --region us-east-1
```

```
> aws --endpoint-url=http://localhost:4572 s3 mb s3://sse-bucket --region us-east-1
```

Now start the data consumer to read in the stream and post data to SQS:

```
> python sse_consumer.py
```

Next, in a separate terminal, run the stream processor so the data is processed and stored in the mocked S3:

```
> python stream_processor.py
```

The tool is now running. To validate that the stream and S3 storage are working, navigate to `localhost:4572/moto-api` and check each service individually.

## Upcoming developments

As recommended in the tutorial, I plan to extend this project to practice and experiment with various data engineering tools. Examples:

* Using `kedro` to structure the tool into a pipeline that is easy to understand and extend.
* Using `kedro-viz` to visualize the pipeline
* Implementing exception handling
* Implementing some more data processing steps before writing the data file. Example: filtering for specific changes (e.g. only to English version of Wikipedia) instead of storing all changes