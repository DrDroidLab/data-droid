from client.source_processors.aws_cloudwatch_processor import AWSCloudwatchProcessor
from client.source_processors.bash_processor import BashProcessor
from client.source_processors.kubectl_processor import KubectlProcessor
from client.source_processors.postgres_db_processor import PostgresDBProcessor


class DataFactory:

    @staticmethod
    def get_bash_client(remote_server: str, pem_passphrase: str = None, pem: str = None):
        return BashProcessor(remote_server, pem_passphrase, pem)

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
