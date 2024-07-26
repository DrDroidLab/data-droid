# Data Droid - Python SDK for fetching data from various sources

This is a library that will allow developers to fetch data from various sources.
Currently supported sources are:

- AWS Cloudwatch (metrics and logs)
- Remote Servers (bash command execution)
- Kubernetes (kubectl command execution)

## Install the SDK

Run this command to get the latest stable version of the SDK (latest version: 0.0.1)

```
pip install data-droid-sdk
```

## Env vars

| Env Var Name     | Description      | Default |   
|------------------|------------------|---------|
| AWS_ACCESS_KEY   | Aws Access key   | ---     |
| AWS_ACCESS_TOKEN | Aws Access Token | ---     |   
| AWS_REGION       | Aws region       | ---     |   

## Configuration

You can connect to any source by providing the necessary credentials as environment variables or directly as arguments
to Data Factory.

## Start fetching data

The sdk exposes a Data Factory class with static access to establishing connection with any of the supported clients.
Once the client is created, it can be used to fetch data from the source.

```python
from pydatadroid import DataFactory

aws_cw_client = DataFactory.get_aws_cloudwatch_client(client_type="logs", region="aws-region",
                                                      aws_access_key="aws-access-key",
                                                      aws_secret_key="aws-secret-key")

if not aws_cw_client.test_connection():
    raise Exception("Connection to AWS Cloudwatch failed")
data = aws_cw_client.logs_filter_events(log_group="log_group_name",
                                        query_pattern="fields @timestamp, @message | limit 1")


```

## Connect with us

Visit [Doctor Droid website](https://drdroid.io?utm_param=github-py) for getting early access.
Go through our [documentation](https://docs.drdroid.io?utm_param=github-py) to learn more.

For any queries, reach out at [mohit.goyal@drdroid.io](mailto:mohit.goyal@drdroid.io).
