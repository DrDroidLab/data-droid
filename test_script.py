# This script is only for dev environment to test the connector that you're adding
from pydatadroid import DataFactory
import yaml
import json


def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def trunc_dict(dictionary_output, limit: int = 100):
    return json.dumps(dictionary_output)[0:min(len(json.dumps(dictionary_output)), limit)]


if __name__ == '__main__':

    config = load_config("test_credentials/credentials.yaml")
    ## create an array of parent keys from the config file
    parent_keys = list(config.keys())
    connectors_count = len(parent_keys)
    print(connectors_count, " keys found in the credentials.yaml file.")
    connectors_tested_count = 0
    failed_tests = []
    # if aws-logs is in the credentials.yaml file
    for tool_cred in parent_keys:
        try:
            if tool_cred == 'aws_logs':
                print("\n Testing AWS Cloudwatch Logs Connector")
                client_type = config.get('aws_logs', {}).get('client_type')
                region = config.get('aws_logs', {}).get('region')
                aws_access_key = config.get('aws_logs', {}).get('aws_access_key')
                aws_secret_key = config.get('aws_logs', {}).get('aws_secret_key')
                aws_cw_logs_client = DataFactory.get_aws_cloudwatch_client(client_type, region, aws_access_key,
                                                                           aws_secret_key)
                if not aws_cw_logs_client.test_connection():
                    raise Exception(f"Connection to {tool_cred} failed")
                else:
                    # Depending on log groups in your AWS account, you can change the log_group value
                    log_group = "/aws/containerinsights/prod/application"
                    query_pattern = "fields @timestamp, @message | limit 1"
                    log_output = aws_cw_logs_client.logs_filter_events(log_group, query_pattern)
                    if log_output:
                        print("\n Sample Log output from AWS Cloudwatch Logs:\n", trunc_dict(log_output))
                    else:
                        print("\n No logs found for the given query")
                    connectors_tested_count += 1
            elif tool_cred == 'aws_metrics':
                client_type = config.get('aws_metrics', {}).get('client_type')
                region = config.get('aws_metrics', {}).get('region')
                aws_access_key = config.get('aws_metrics', {}).get('aws_access_key')
                aws_secret_key = config.get('aws_metrics', {}).get('aws_secret_key')
                aws_cw_client = DataFactory.get_aws_cloudwatch_client(client_type, region, aws_access_key,
                                                                      aws_secret_key)
                if not aws_cw_client.test_connection():
                    raise Exception(f"Connection to {tool_cred} failed")
                else:
                    print(f"\n Credentials successfully tested for {tool_cred}. Now running a sample query")
                    # Depending on the metric you want to query, you can change the namespace, metric and dimensions values
                    namespace = "AWS/RDS"
                    metric = "CPUUtilization"
                    dimensions = {"EngineName": "postgres"}
                    metric_output = aws_cw_client.cloudwatch_get_metric_statistics(namespace, metric, dimensions)
                    print("\n Sample Metric output from AWS Cloudwatch Metrics:\n", trunc_dict(metric_output))
                    connectors_tested_count += 1
            elif tool_cred == 'kubectl_connector':
                print("\n Testing Kubectl Connector")
                api_server = config.get('kubectl_connector', {}).get('api_server')
                token = config.get('kubectl_connector', {}).get('token')
                ssl_ca_cert_data = config.get('kubectl_connector', {}).get('ssl_ca_cert_data')
                kubectl_client = DataFactory.get_kubectl_client(api_server, token, ssl_ca_cert_data)
                if not kubectl_client.test_connection():
                    raise Exception(f"Connection to {tool_cred} failed")
                else:
                    print(f"\n Credentials successfully tested {tool_cred}. Now running a sample query")
                    kubectl_output = kubectl_client.execute_command("kubectl get pods -A")
                    print("\n Sample output from Kubectl command:\n", trunc_dict(kubectl_output))
                    connectors_tested_count += 1
            elif tool_cred == 'bash_command_server':
                print("\n Testing Bash Command Connector")
                remote_server = config.get('bash_command_server', {}).get('remote_server')
                client_pem_path = config.get('bash_command_server', {}).get('pem_path')
                bash_client = DataFactory.get_bash_client(remote_server, pem_path=client_pem_path)
                if not bash_client.test_connection():
                    raise Exception(f"Connection to {tool_cred} failed")
                else:
                    print(f"\n Credentials successfully tested for {tool_cred}. Now running a sample command")
                    bash_output = bash_client.execute_commands(["sudo docker ps"])
                    print("\n Sample output from Bash Command:\n", trunc_dict(bash_output))
                    connectors_tested_count += 1
            elif tool_cred == 'postgres_db':
                print("\n Testing Postgres DB Connector")
                host = config.get('postgres_db', {}).get('host')
                user = config.get('postgres_db', {}).get('user')
                password = config.get('postgres_db', {}).get('password')
                database = config.get('postgres_db', {}).get('database')
                port = config.get('postgres_db', {}).get('port')
                connect_timeout = config.get('postgres_db', {}).get('connect_timeout')
                postgres_client = DataFactory.get_postgres_db_client(host, user, password, database, port,
                                                                     connect_timeout)
                if not postgres_client.test_connection():
                    raise Exception(f"Connection to {tool_cred} failed")
                else:
                    print(f"\n Credentials successfully tested for {tool_cred}. Now running a sample query")
                    query = "SELECT * FROM pg_stat_activity"
                    postgres_output = postgres_client.get_query_result(query)
                    print("\n Sample output from Postgres DB:\n", trunc_dict(postgres_output))
                    connectors_tested_count += 1
            elif tool_cred == 'grafana_loki':
                print("\n Testing Grafana Loki Connector")
                host = config.get('grafana_loki', {}).get('host')
                port = config.get('grafana_loki', {}).get('port')
                protocol = config.get('grafana_loki', {}).get('protocol')
                x_scope_org_id = config.get('grafana_loki', {}).get('x_scope_org_id')
                ssl_verify = config.get('grafana_loki', {}).get('ssl_verify', True)
                loki_client = DataFactory.get_grafana_loki_client(host, port, protocol, x_scope_org_id, ssl_verify)
                if not loki_client.test_connection():
                    raise Exception(f"Connection to {tool_cred} failed")
                else:
                    print(f"\n Credentials successfully tested for {tool_cred}. Now running a sample query")
                    query = '{job="python-logger"}'
                    loki_output = loki_client.query(query)
                    print("\n Sample output from Grafana Loki:\n", trunc_dict(loki_output))
                    connectors_tested_count += 1
            elif tool_cred == 'grafana_promql':
                print("\n Testing Grafana promql Connector")
                host = config.get('grafana_promql', {}).get('host')
                port = config.get('grafana_promql', {}).get('port')
                protocol = config.get('grafana_promql', {}).get('protocol')
                api_key = config.get('grafana_promql', {}).get('api_key')
                ssl_verify = config.get('grafana_promql', {}).get('ssl_verify', True)
                promql_client = DataFactory.get_grafana_promql_client(host, port, protocol, api_key, ssl_verify)
                if not promql_client.test_connection():
                    raise Exception(f"Connection to {tool_cred} failed")
                else:
                    print(f"\n Credentials successfully tested for {tool_cred}. Now running a sample query")
                    datasource_uid = "dbfa7a5f-f8bd-49f2-8ea3-8e16832d572a"
                    query = 'sum(rate(status_counter[1m]))'
                    promql_output = promql_client.query(datasource_uid, query)
                    print("\n Sample output from grafana_promql:\n", trunc_dict(promql_output))
                    connectors_tested_count += 1
            elif tool_cred == 'grafana_mimir':
                print("\n Testing Grafana Mimir Connector")
                host = config.get('grafana_mimir', {}).get('host')
                port = config.get('grafana_mimir', {}).get('port')
                protocol = config.get('grafana_mimir', {}).get('protocol')
                x_scope_org_id = config.get('grafana_mimir', {}).get('x_scope_org_id')
                ssl_verify = config.get('grafana_mimir', {}).get('ssl_verify', True)
                mimir_client = DataFactory.get_grafana_mimir_client(host, port, protocol, x_scope_org_id, ssl_verify)
                if not mimir_client.test_connection():
                    raise Exception(f"Connection to {tool_cred} failed")
                else:
                    print(f"\n Credentials successfully tested for {tool_cred}. Now running a sample query")
                    query = 'histogram_quantile(0.99, sum by (le) (cluster_job_route:cortex_request_duration_seconds_bucket:sum_rate{cluster=~"demo", job=~"(demo)/((distributor.|cortex|mimir|mimir-write.))", route=~"/distributor.Distributor/Push|/httpgrpc.*|api_(v1|prom)_push|otlp_v1_metrics"})) * 1e3'
                    mimir_output = mimir_client.query(query)
                    print("\n Sample output from Grafana Mimir:\n", trunc_dict(mimir_output))
                    connectors_tested_count += 1
            elif tool_cred == 'clickhouse':
                print("\n Testing Clickhouse Connector")
                protocol = config.get('clickhouse', {}).get('protocol')
                host = config.get('clickhouse', {}).get('host')
                port = config.get('clickhouse', {}).get('port')
                user = config.get('clickhouse', {}).get('user')
                password = config.get('clickhouse', {}).get('password')
                database = config.get('clickhouse', {}).get('database')
                clickhouse_client = DataFactory.get_clickhouse_db_client(protocol, host, port, user, password, database)
                if not clickhouse_client.test_connection():
                    raise Exception(f"Connection to {tool_cred} failed")
                else:
                    print(f"\n Credentials successfully tested for {tool_cred}. Now running a sample query")
                    # Add your query here
                    query = 'select * from ontime limit 1'
                    clickhouse_output = clickhouse_client.get_query_result(query)
                    print("\n Sample output from Clickhouse DB:\n", trunc_dict(clickhouse_output))
                    connectors_tested_count += 1
            elif tool_cred == 'datadog':
                print("\n Testing Datadog Connector")
                dd_app_key = config.get('datadog', {}).get('dd_app_key')
                dd_api_key = config.get('datadog', {}).get('dd_api_key')
                dd_api_domain = config.get('datadog', {}).get('dd_api_domain')

                datadog_client = DataFactory.get_datadog_client(dd_app_key, dd_api_key, dd_api_domain)
                if not datadog_client.test_connection():
                    raise Exception(f"Connection to {tool_cred} failed")
                else:
                    print(f"\n Credentials successfully tested for {tool_cred}. Now running a sample query")
                    # Add your query here
                    queries = ['avg:trace.django.request{env:prod}']

                    datadog_output = datadog_client.fetch_metric_timeseries(queries)
                    print("\n Sample output from Datadog:\n", trunc_dict(datadog_output))
                    connectors_tested_count += 1
            elif tool_cred == 'db_connection_string':
                print("\n Testing Database String Connector")
                connection_string = config.get('db_connection_string', {}).get('connection_string')
                db_str_client = DataFactory.get_db_connection_string_client(connection_string)
                if not db_str_client.test_connection():
                    raise Exception(f"Connection to {tool_cred} failed")
                else:
                    print(f"\n Credentials successfully tested for {tool_cred}. Now running a sample query")
                    # Add your query here
                    query = 'select * from management_task limit 1'

                    db_str_output = db_str_client.get_query_result(query)
                    print("\n Sample output from Database String:\n", trunc_dict(db_str_output))
                    connectors_tested_count += 1
            elif tool_cred == 'eks':
                print("\n Testing EKS Connector")
                region = config.get('eks', {}).get('region')
                aws_access_key = config.get('eks', {}).get('aws_access_key')
                aws_secret_key = config.get('eks', {}).get('aws_secret_key')
                k8_role_arn = config.get('eks', {}).get('k8_role_arn')

                eks_client = DataFactory.get_eks_client(region, aws_access_key, aws_secret_key, k8_role_arn)
                if not eks_client.test_connection():
                    raise Exception(f"Connection to {tool_cred} failed")
                else:
                    print(f"\n Credentials successfully tested for {tool_cred}. Now running a sample query")
                    # Add your query here
                    kubectl_command = 'kubectl get pods -A'

                    eks_output = eks_client.execute_kubectl_command(cluster='prod', command=kubectl_command)
                    print("\n Sample output from EKS:\n", trunc_dict(eks_output))
                    connectors_tested_count += 1
            elif tool_cred == 'gke':
                print("\n Testing GKE Connector")
                project_id = config.get('gke', {}).get('project_id')
                service_account_json = config.get('gke', {}).get('service_account_json')
                gke_client = DataFactory.get_gke_client(project_id, service_account_json)
                if not gke_client.test_connection():
                    raise Exception(f"Connection to {tool_cred} failed")
                else:
                    print(f"\n Credentials successfully tested for {tool_cred}. Now running a sample query")
                    # Add your query here
                    kubectl_command = 'kubectl get pods -A'

                    gke_output = gke_client.execute_kubectl_command(zone='us-central1', cluster='helm-test',
                                                                    command=kubectl_command)
                    print("\n Sample output from GKE:\n", trunc_dict(gke_output))
                    connectors_tested_count += 1
            elif tool_cred == 'new_relic':
                print("\n Testing New Relic Connector")
                nr_api_key = config.get('new_relic', {}).get('nr_api_key')
                nr_account_id = config.get('new_relic', {}).get('nr_account_id')
                nr_api_domain = config.get('new_relic', {}).get('nr_api_domain', 'api.newrelic.com')

                nr_client = DataFactory.get_new_relic_client(nr_api_key, nr_account_id, nr_api_domain)
                if not nr_client.test_connection():
                    raise Exception(f"Connection to {tool_cred} failed")
                else:
                    print(f"\n Credentials successfully tested for {tool_cred}. Now running a sample query")
                    # Add your query here
                    nrql_expression = "SELECT rate(count(newrelic.goldenmetrics.apm.application.throughput), 1 MINUTES) AS 'Throughput' FROM Metric WHERE entity.guid in ('MzY2MjU4OXxBUE18QVBQTElDQVRJT058MTAyOTA0MjA3Mg') LIMIT MAX TIMESERIES"
                    nr_output = nr_client.execute_nrql_query(nrql_expression)
                    print("\n Sample output from New Relic:\n", trunc_dict(nr_output))
                    connectors_tested_count += 1
            else:
                print(f"\n {tool_cred} credentials found in YAML but not configured for testing."
                      f"Moving to the next connector testing.")
        except Exception as e:
            print(f"Error in testing code in {tool_cred} connector: ", e)
            failed_tests.append(tool_cred)
            continue
    print("\n\n", connectors_tested_count, " connectors tested successfully out of ", connectors_count)
    print("Failed tests: ", failed_tests)
