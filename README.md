# Data Droid - Python SDK for fetching data from various sources

This is a library that will allow developers to fetch data from various sources.
Currently supported sources are:

- AWS Cloudwatch (metrics and logs)
- Remote Servers (bash command execution)
- Kubernetes (kubectl command execution)
- Postgres (DB queries)

## Install the SDK

Run this command to get the latest stable version of the SDK (latest version: 0.0.1)

```
pip install data-droid-sdk
```

## Using the SDK

The sdk exposes a Data Factory class with static access to establishing connection with any of the supported clients.
Once the client is created, it can be used to fetch data from the source.

First you need to create a connector:

```python
from pydatadroid import DataFactory

aws_cw_client = DataFactory.get_aws_cloudwatch_client(client_type="logs", region="aws-region",
                                                      aws_access_key="aws-access-key",
                                                      aws_secret_key="aws-secret-key")

if not aws_cw_client.test_connection():
    raise Exception("Connection to AWS Cloudwatch failed")
```

The next step is to query data on the connector
```
data = aws_cw_client.logs_filter_events(log_group="log_group_name",
                                        query_pattern="fields @timestamp, @message | limit 1")
```

The output is currently stored as a dictionary. We are following 6 standard formats basis the type of data. Read more about it [here](https://docs.drdroid.io/docs/data-output-formats).

## Contributing

To add a new connector:
- create a new file in source_processors folder for your tool
- add a function in lib.py that will work for this connection
- ensure to comply to the Protos defined in protos/result.proto for the output formats of the connector
- add a test case in test_script.py and sample credential format in test_credentials/credentials_template.yaml
- Run the file test_script.py with command 'python test_script.py' in parent directory and ensure you're able to successfully test the tool's integration

## Have questions?
Join our [Slack community](https://join.slack.com/t/doctor-droid-demo/shared_invite/zt-2h6eap61w-Bmz76OEU6IykmDy673R1qQ).


## Like what you see? Don't forget to star the repo and support us!