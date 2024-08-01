from pydatadroid.source_processors.aws_cloudwatch_processor import AWSCloudwatchProcessor
from pydatadroid.source_processors.bash_processor import BashProcessor
from pydatadroid.source_processors.kubectl_processor import KubectlProcessor
from pydatadroid.source_processors.postgres_db_processor import PostgresDBProcessor
from pydatadroid.source_processors.grafana_loki_processor import GrafanaLokiApiProcessor
from pydatadroid.source_processors.grafana_promql_processor import GrafanaPromqlProcessor
from pydatadroid.source_processors.grafana_mimir_processor import GrafanaMimirApiProcessor

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
    def get_grafana_loki_client(host: str, port: int, protocol: str, x_scope_org_id: str='anonymous', ssl_verify: bool=True):
        return GrafanaLokiApiProcessor(host, port, protocol, x_scope_org_id, ssl_verify)
    
    @staticmethod
    def get_grafana_mimir_client(host: str,port: int,protocol: str, x_scope_org_id='anonymous', ssl_verify='true'):
        return GrafanaMimirApiProcessor(host, port, protocol, x_scope_org_id, ssl_verify)
    
    @staticmethod
    def get_grafana_promql_client(host: str, port: int, protocol: str, api_key: str, ssl_verify: bool=True):
        return GrafanaPromqlProcessor(host, port, protocol, api_key, ssl_verify)