from source_processors.aws_cloudwatch_processor import AWSCloudwatchProcessor
from source_processors.bash_processor import BashProcessor


class ClientFactory:

    @staticmethod
    def get_bash_client(remote_server: str, pem_passphrase: str = None, pem: str = None):
        return BashProcessor(remote_server, pem_passphrase, pem)

    @staticmethod
    def get_aws_cloudwatch_client(client_type: str, region: str, aws_access_key: str, aws_secret_key: str):
        return AWSCloudwatchProcessor(client_type, region, aws_access_key, aws_secret_key)
