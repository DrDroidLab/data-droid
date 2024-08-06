from typing import Dict

from pydatadroid.source_processors.aws_cloudwatch_processor import AWSCloudwatchProcessor
from pydatadroid.source_processors.azure_processor import AzureProcessor
from pydatadroid.source_processors.bash_processor import BashProcessor
from pydatadroid.source_processors.clickhouse_db_processor import ClickhouseDBProcessor
from pydatadroid.source_processors.datadog_processor import DatadogProcessor
from pydatadroid.source_processors.db_connection_string_processor import DBConnectionStringProcessor
from pydatadroid.source_processors.eks_processor import EksProcessor
from pydatadroid.source_processors.elastic_search_provcessor import ElasticSearchProcessor
from pydatadroid.source_processors.gke_processor import GkeProcessor
from pydatadroid.source_processors.kubectl_processor import KubectlProcessor
from pydatadroid.source_processors.new_relic_processor import NewRelicProcessor
from pydatadroid.source_processors.postgres_db_processor import PostgresDBProcessor
from pydatadroid.source_processors.grafana_loki_processor import GrafanaLokiProcessor
from pydatadroid.source_processors.grafana_promql_processor import GrafanaPromqlProcessor
from pydatadroid.source_processors.grafana_mimir_processor import GrafanaMimirProcessor


class DataFactory:

    @staticmethod
    def get_bash_client(remote_server: str, pem_passphrase: str = None, pem_str: str = None, pem_path: str = None):
        return BashProcessor(remote_server, pem_passphrase, pem_str, pem_path)

    @staticmethod
    def get_aws_cloudwatch_client(client_type: str, region: str, aws_access_key: str, aws_secret_key: str):
        return AWSCloudwatchProcessor(client_type, region, aws_access_key, aws_secret_key)

    @staticmethod
    def get_kubectl_client(api_server: str, token: str, ssl_ca_cert_data: str = None, ssl_ca_cert_path: str = None):
        return KubectlProcessor(api_server, token, ssl_ca_cert_data, ssl_ca_cert_path)

    @staticmethod
    def get_postgres_db_client(host: str, user: str, password: str, database: str, port: int = 5432,
                               connect_timeout: int = None):
        return PostgresDBProcessor(host, user, password, database, port, connect_timeout)

    @staticmethod
    def get_grafana_loki_client(host: str, port: int, protocol: str, x_scope_org_id: str = 'anonymous',
                                ssl_verify: bool = True):
        return GrafanaLokiProcessor(host, port, protocol, x_scope_org_id, ssl_verify)

    @staticmethod
    def get_grafana_mimir_client(host: str, port: int, protocol: str, x_scope_org_id: str = 'anonymous',
                                 ssl_verify: bool = True):
        return GrafanaMimirProcessor(host, port, protocol, x_scope_org_id, ssl_verify)

    @staticmethod
    def get_grafana_promql_client(host: str, port: int, protocol: str, api_key: str, ssl_verify: bool = True):
        return GrafanaPromqlProcessor(host, port, protocol, api_key, ssl_verify)

    @staticmethod
    def get_azure_client(subscription_id: str, tenant_id: str, client_id: str, client_secret: str):
        return AzureProcessor(subscription_id, tenant_id, client_id, client_secret)

    @staticmethod
    def get_clickhouse_db_client(protocol: str, host: str, port: str, user: str, password: str, database: str):
        return ClickhouseDBProcessor(protocol, host, port, user, password, database)

    @staticmethod
    def get_datadog_client(dd_app_key: str, dd_api_key: str, dd_api_domain: str = 'datadoghq.com'):
        return DatadogProcessor(dd_app_key, dd_api_key, dd_api_domain)

    @staticmethod
    def get_db_connection_string_client(connection_string: str):
        return DBConnectionStringProcessor(connection_string)

    @staticmethod
    def get_eks_client(region: str, aws_access_key: str, aws_secret_key: str, k8_role_arn: str,
                       aws_session_token: str = None):
        return EksProcessor(region, aws_access_key, aws_secret_key, k8_role_arn, aws_session_token)

    @staticmethod
    def get_elastic_search_client(protocol: str, host: str, port: str, api_key_id: str, api_key: str,
                                  verify_certs: bool = False):
        return ElasticSearchProcessor(protocol, host, port, api_key_id, api_key, verify_certs)

    @staticmethod
    def get_new_relic_client(nr_api_key: str, nr_account_id: str, nr_api_domain: str = 'api.newrelic.com'):
        return NewRelicProcessor(nr_api_key, nr_account_id, nr_api_domain)

    @staticmethod
    def get_gke_client(project_id: str, service_account_json: Dict):
        return GkeProcessor(project_id, service_account_json)
