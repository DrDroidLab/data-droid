from source_processors.aws_cloudwatch_processor import AWSCloudwatchProcessor
from source_processors.bash_processor import BashProcessor
from source_processors.kubectl_processor import KubectlProcessor


class ClientFactory:

    @staticmethod
    def get_bash_client(remote_server: str, pem_passphrase: str = None, pem: str = None):
        return BashProcessor(remote_server, pem_passphrase, pem)

    @staticmethod
    def get_aws_cloudwatch_client(client_type: str, region: str, aws_access_key: str, aws_secret_key: str):
        return AWSCloudwatchProcessor(client_type, region, aws_access_key, aws_secret_key)

    @staticmethod
    def get_kubectl_client(api_server: str, token: str, ssl_ca_cert: str = None, ssl_ca_cert_path: str = None):
        return KubectlProcessor(api_server, token, ssl_ca_cert, ssl_ca_cert_path)
