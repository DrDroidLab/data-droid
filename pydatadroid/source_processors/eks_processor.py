import base64
import logging
import tempfile
from abc import ABC
from datetime import datetime, timedelta

import boto3
import kubernetes as kubernetes
from awscli.customizations.eks.get_token import TOKEN_EXPIRATION_MINS, STSClientFactory, TokenGenerator

from pydatadroid.protos.result_pb2 import Result, ResultType, BashCommandOutputResult
from pydatadroid.source_processors.kubectl_processor import KubectlProcessor
from pydatadroid.source_processors.processor import Processor
from pydatadroid.utils.proto_utils import proto_to_dict, dict_to_proto

logger = logging.getLogger(__name__)


def get_expiration_time():
    token_expiration = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRATION_MINS)
    return token_expiration.strftime('%Y-%m-%dT%H:%M:%SZ')


def get_eks_token(cluster_name: str, aws_access_key: str, aws_secret_key: str, region: str,
                  role_arn: str = None, aws_session_token=None) -> dict:
    aws_session = boto3.Session(
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=region,
        aws_session_token=aws_session_token
    )
    client_factory = STSClientFactory(aws_session._session)
    sts_client = client_factory.get_sts_client(role_arn=role_arn)
    token = TokenGenerator(sts_client).get_token(cluster_name)
    return token


class EksProcessor(Processor, ABC):
    def __init__(self, region: str, aws_access_key: str, aws_secret_key: str, k8_role_arn: str, aws_session_token=None):
        self.__aws_access_key = aws_access_key
        self.__aws_secret_key = aws_secret_key
        self.region = region
        self.__k8_role_arn = k8_role_arn
        self.__aws_session_token = aws_session_token

    def get_connection(self):
        try:
            client = boto3.client('eks', aws_access_key_id=self.__aws_access_key,
                                  aws_secret_access_key=self.__aws_secret_key, region_name=self.region,
                                  aws_session_token=self.__aws_session_token)
            return client
        except Exception as e:
            logger.error(f"Exception occurred while creating boto3 client with error: {e}")
            raise e

    def test_connection(self):
        try:
            client = self.get_connection()
            clusters = client.list_clusters()['clusters']
            if clusters:
                return True
            else:
                raise Exception("No clusters found in the eks connection")
        except Exception as e:
            logger.error(f"Exception occurred while testing cloudwatch connection with error: {e}")
            raise e

    def _eks_describe_cluster(self, cluster_name):
        try:
            client = self.get_connection()
            cluster_details = client.describe_cluster(name=cluster_name)['cluster']
            return cluster_details
        except Exception as e:
            logger.error(f"Exception occurred while fetching EKS clusters with error: {e}")
            raise e

    def _eks_get_api_instance(self, cluster, client='api'):
        eks_details = self._eks_describe_cluster(cluster)

        fp = tempfile.NamedTemporaryFile(delete=False)
        ca_filename = fp.name
        cert_bs = base64.urlsafe_b64decode(eks_details['certificateAuthority']['data'].encode('utf-8'))
        fp.write(cert_bs)
        fp.close()

        # Token for the EKS cluster
        token = get_eks_token(cluster, self.__aws_access_key, self.__aws_secret_key, self.region,
                              self.__k8_role_arn, self.__aws_session_token)
        if not token:
            raise Exception(f"Error occurred while fetching token for EKS cluster: {cluster}")

        # Kubernetes client config
        conf = kubernetes.client.Configuration()
        conf.host = eks_details['endpoint']
        conf.api_key['authorization'] = token
        conf.api_key_prefix['authorization'] = 'Bearer'
        conf.ssl_ca_cert = ca_filename
        with kubernetes.client.ApiClient(conf) as api_client:
            if client == 'api':
                api_instance = kubernetes.client.CoreV1Api(api_client)
                return api_instance
            elif client == 'app':
                app_instance = kubernetes.client.AppsV1Api(api_client)
                return app_instance

    def _get_kubectl_processor(self, cluster, client='api'):
        api_instance = self._eks_get_api_instance(cluster=cluster, client=client)
        eks_host = api_instance.api_client.configuration.host
        token = api_instance.api_client.configuration.api_key.get('authorization')
        ssl_ca_cert_path = api_instance.api_client.configuration.ssl_ca_cert
        return KubectlProcessor(api_server=eks_host, token=token, ssl_ca_cert_path=ssl_ca_cert_path)

    def execute_kubectl_command(self, cluster, command):
        try:
            commands = command.split('\n')
            kubectl_client = self._get_kubectl_processor(cluster, 'api')
            command_output_protos = []
            for command in commands:
                command_to_execute = command
                output = kubectl_client.execute_command(command_to_execute)
                bash_output_proto = dict_to_proto(output, Result)
                command_output_protos.extend(bash_output_proto.bash_command_output.command_outputs)

            task_result = Result(
                type=ResultType.BASH_COMMAND_OUTPUT,
                bash_command_output=BashCommandOutputResult(command_outputs=command_output_protos)
            )
            return proto_to_dict(task_result)
        except Exception as e:
            raise Exception(f"Error while executing EKS kubectl task: {e}")
