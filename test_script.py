# This script is only for dev environment to test the connector that you're adding


from pydatadroid import DataFactory

import yaml

def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


if __name__ == '__main__':
    
    config = load_config("test_credentials/credentials.yaml")
    ## if aws-logs is in the credentials.yaml file
    try:
        if 'aws_logs' in config:
            print("\n Testing AWS Logs Connector")
            client_type = config.get('aws_logs',{}).get('client_type')
            region = config.get('aws_logs',{}).get('region')
            aws_access_key = config.get('aws_logs',{}).get('aws_access_key')
            aws_secret_key = config.get('aws_logs',{}).get('aws_secret_key')
            aws_cw_logs_client = DataFactory.get_aws_cloudwatch_client(client_type, region, aws_access_key, aws_secret_key)
            if not aws_cw_logs_client.test_connection():
                raise Exception("Connection to AWS Cloudwatch failed")
            else:
                print("\n Credentials successfully tested. Now running a sample query")
                ## Depending on log groups in your AWS account, you can change the log_group value
                log_group="/aws/containerinsights/prod/application"
                query_pattern="fields @timestamp, @message | limit 1"
                log_output = aws_cw_logs_client.logs_filter_events(log_group,query_pattern)
                if log_output:
                    print("\n Sample Log output from AWS Cloudwatch Logs:\n", log_output)
                else:
                    print("\n No logs found for the given query")
        else:
            print("\n aws_logs credentials not found in the credentials.yaml file. Moving to the next connector testing.")
    except Exception as e:
        print("\n Check test_script.py . Error in Testing code in aws_logs connector: ", e)

    try:
        if 'aws_metrics' in config:
            print("\n Testing AWS Metrics Connector")
            client_type = config.get('aws_metrics',{}).get('client_type')
            region = config.get('aws_metrics',{}).get('region')
            aws_access_key = config.get('aws_metrics',{}).get('aws_access_key')
            aws_secret_key = config.get('aws_metrics',{}).get('aws_secret_key')
            aws_cw_client = DataFactory.get_aws_cloudwatch_client(client_type, region, aws_access_key, aws_secret_key)
            if not aws_cw_client.test_connection():
                raise Exception("Connection to AWS Cloudwatch failed")
            else:
                print("\n Credentials successfully tested. Now running a sample query")
                # Depending on the metric you want to query, you can change the namespace, metric and dimensions values
                namespace = "AWS/RDS"
                metric = "CPUUtilization"
                dimensions = {"EngineName": "postgres"}
                metric_output = aws_cw_client.cloudwatch_get_metric_statistics(namespace, metric,dimensions)
                print("\n Sample Metric output from AWS Cloudwatch Metrics:\n", metric_output)
        else:
            print("\n aws_metrics credentials not found in the credentials.yaml file. Moving to the next connector testing.")
    except Exception as e:
        print("\n Check test_script.py . Error in Testing code in aws_metrics connector: ", e)


    try:
        if 'kubectl_connector' in config:
            print("\n Testing Kubectl Connector")
            api_server = config.get('kubectl_connector',{}).get('api_server')
            token = config.get('kubectl_connector',{}).get('token')
            ssl_ca_cert_data = config.get('kubectl_connector',{}).get('ssl_ca_cert_data')
            kubectl_client = DataFactory.get_kubectl_client(api_server, token, ssl_ca_cert_data)
            if not kubectl_client.test_connection():
                raise Exception("Connection to Kubectl failed")
            else:
                print("\n Credentials successfully tested. Now running a sample query")
                kubectl_output = kubectl_client.execute_command("kubectl get pods -A")
                print("\n Sample output from Kubectl command:\n", kubectl_output)
        else:
            print("\n kubectl_connector credentials not found in the credentials.yaml file. Moving to the next connector testing.")
    except Exception as e:
        print("\n Check test_script.py . Error in Testing code in kubectl_connector: ", e)

    try:
        if 'bash_command_server' in config:
            print("\n Testing Bash Command Connector")
            remote_server = config.get('bash_command_server',{}).get('remote_server')
            client_pem_path = config.get('bash_command_server',{}).get('pem_path')
            bash_client = DataFactory.get_bash_client(remote_server, pem_path=client_pem_path)
            if not bash_client.test_connection():
                raise Exception("Connection to Bash Command Server failed")
            else:
                print("\n Credentials successfully tested. Now running a sample command")
                bash_output = bash_client.execute_commands(["sudo docker ps"])
                print("\n Sample output from Bash Command:\n", bash_output)
        else:
            print("\n bash_command_server credentials not found in the credentials.yaml file. Moving to the next connector testing.")
    except Exception as e:
        print("\n Check test_script.py . Error in Testing code in bash_command_server: ", e)

    try:
        if 'postgres_db' in config:
            print("\n Testing Postgres DB Connector")
            host = config.get('postgres_db',{}).get('host')
            user = config.get('postgres_db',{}).get('user')
            password = config.get('postgres_db',{}).get('password')
            database = config.get('postgres_db',{}).get('database')
            port = config.get('postgres_db',{}).get('port')
            connect_timeout = config.get('postgres_db',{}).get('connect_timeout')
            postgres_client = DataFactory.get_postgres_db_client(host, user, password, database, port, connect_timeout)
            if not postgres_client.test_connection():
                raise Exception("Connection to Postgres DB failed")
            else:
                print("\n Credentials successfully tested. Now running a sample query")
                query = "SELECT * FROM pg_stat_activity"
                postgres_output = postgres_client.get_query_result(query)
                print("\n Sample output from Postgres DB:\n", postgres_output)
        else:
            print("\n postgres_db credentials not found in the credentials.yaml file. Moving to the next connector testing.")
    except Exception as e:
        print("\n Check test_script.py . Error in Testing code in postgres_db: ", e)

    try:
        if 'grafana_loki' in config:
            print("\n Testing Grafana Loki Connector")
            host = config.get('grafana_loki',{}).get('host')
            port = config.get('grafana_loki',{}).get('port')
            protocol = config.get('grafana_loki',{}).get('protocol')
            x_scope_org_id = config.get('grafana_loki',{}).get('x_scope_org_id')
            ssl_verify = config.get('grafana_loki',{}).get('ssl_verify',True)
            loki_client = DataFactory.get_grafana_loki_client(host, port, protocol, x_scope_org_id, ssl_verify)
            if not loki_client.test_connection():
                raise Exception("Connection to Grafana Loki failed")
            else:
                print("\n Credentials successfully tested. Now running a sample query")
                query = '{job="python-logger"}'
                loki_output = loki_client.query(query)
                print("\n Sample output from Grafana Loki:\n", loki_output)
        else:
            print("\n grafana_loki credentials not found in the credentials.yaml file. Moving to the next connector testing.")
    except Exception as e:
        print("\n Check test_script.py . Error in Testing code in grafana_loki: ", e)

    try:
        if 'grafana_promql' in config:
            print("\n Testing Grafana promql Connector")
            host = config.get('grafana_promql',{}).get('host')
            port = config.get('grafana_promql',{}).get('port')
            protocol = config.get('grafana_promql',{}).get('protocol')
            api_key = config.get('grafana_promql',{}).get('api_key')
            ssl_verify = config.get('grafana_promql',{}).get('ssl_verify',True)
            promql_client = DataFactory.get_grafana_promql_client(host, port, protocol, api_key, ssl_verify)
            if not promql_client.test_connection():
                raise Exception("Connection to Grafana promql failed")
            else:
                print("\n Credentials successfully tested. Now running a sample query")
                datasource_uid = "dbfa7a5f-f8bd-49f2-8ea3-8e16832d572a"
                query = 'sum(rate(status_counter[1m]))'
                promql_output = promql_client.query(datasource_uid, query)
                print("\n Sample output from grafana_promql:\n", promql_output)
        else:
            print("\n grafana_promql credentials not found in the credentials.yaml file. Moving to the next connector testing.")
    except Exception as e:
        print("\n Check test_script.py . Error in Testing code in grafana_promql: ", e)
    
    try:
        if 'grafana_mimir' in config:
            print("\n Testing Grafana Mimir Connector")
            host = config.get('grafana_mimir',{}).get('host')
            port = config.get('grafana_mimir',{}).get('port')
            protocol = config.get('grafana_mimir',{}).get('protocol')
            x_scope_org_id = config.get('grafana_mimir',{}).get('x_scope_org_id')
            ssl_verify = config.get('grafana_mimir',{}).get('ssl_verify',True)
            mimir_client = DataFactory.get_grafana_mimir_client(host, port, protocol, x_scope_org_id, ssl_verify)
            if not mimir_client.test_connection():
                raise Exception("Connection to Grafana Mimir failed")
            else:
                print("\n Credentials successfully tested. Now running a sample query")
                query = 'histogram_quantile(0.99, sum by (le) (cluster_job_route:cortex_request_duration_seconds_bucket:sum_rate{cluster=~"demo", job=~"(demo)/((distributor.|cortex|mimir|mimir-write.))", route=~"/distributor.Distributor/Push|/httpgrpc.*|api_(v1|prom)_push|otlp_v1_metrics"})) * 1e3'
                mimir_output = mimir_client.query(query)
                print("\n Sample output from Grafana Mimir:\n", mimir_output)
        else:
            print("\n grafana_mimir credentials not found in the credentials.yaml file. Moving to the next connector testing.")
    except Exception as e:
        print("\n Check test_script.py . Error in Testing code in grafana_mimir: ", e)
    