import base64
import logging
import tempfile
from abc import ABC

import kubernetes as kubernetes
from google.auth.transport.requests import Request, AuthorizedSession
from google.oauth2 import service_account
from googleapiclient.discovery import build

from pydatadroid.protos.result_pb2 import Result, ResultType, BashCommandOutputResult
from pydatadroid.source_processors.kubectl_processor import KubectlProcessor
from pydatadroid.source_processors.processor import Processor
from pydatadroid.utils.proto_utils import proto_to_dict, dict_to_proto

logger = logging.getLogger(__name__)


def get_gke_credentials(service_account_json):
    scopes = ["https://www.googleapis.com/auth/cloud-platform", "https://www.googleapis.com/auth/userinfo.email"]
    credentials = service_account.Credentials.from_service_account_info(service_account_json, scopes=scopes)

    # Refresh the credentials
    auth_req = Request()
    credentials.refresh(auth_req)

    return credentials


class GkeProcessor(Processor, ABC):
    def __init__(self, project_id, service_account_json):
        self.__service_account_json = service_account_json
        self.__project_id = project_id

    def get_connection(self):
        try:
            credentials = get_gke_credentials(self.__service_account_json)

            service = build('container', 'v1', credentials=credentials)
            return service
        except Exception as e:
            logger.error(f"Exception occurred while creating boto3 client with error: {e}")
            raise e

    def test_connection(self):
        try:
            service = self.get_connection()
            clusters_list = []
            parent = f'projects/{self.__project_id}/locations/-'
            request = service.projects().locations().clusters().list(parent=parent)

            response = request.execute()
            clusters = response.get('clusters', [])
            for cluster in clusters:
                clusters_list.append({
                    'name': cluster['name'],
                    'location': cluster['location'],
                    'status': cluster['status']
                })
            if len(clusters_list) > 0:
                return True
            else:
                raise Exception("Failed to connect with GKE. No clusters found")
        except Exception as e:
            logger.error(f"Exception occurred while fetching grafana data sources with error: {e}")
            raise e

    def _gke_get_api_instance(self, zone: str, cluster: str, client: str = 'api'):
        try:
            credentials = get_gke_credentials(self.__service_account_json)
            cluster_url = f"https://container.googleapis.com/v1/projects/{self.__project_id}/locations/{zone}/clusters/{cluster}"
            authed_session = AuthorizedSession(credentials)
            response = authed_session.request('GET', cluster_url)
            cluster_data = response.json()

            endpoint = cluster_data['endpoint']
            ca_certificate = cluster_data['masterAuth']['clusterCaCertificate']

            fp = tempfile.NamedTemporaryFile(delete=False)
            ca_filename = fp.name
            ca_cert_bytes = base64.b64decode(ca_certificate)
            fp.write(ca_cert_bytes)
            fp.close()

            # Kubernetes client config
            conf = kubernetes.client.Configuration()
            conf.host = f"https://{endpoint}"
            conf.api_key['authorization'] = credentials.token
            conf.api_key_prefix['authorization'] = 'Bearer'
            conf.ssl_ca_cert = ca_filename
            conf.verify_ssl = True
            with kubernetes.client.ApiClient(conf) as api_client:
                if client == 'api':
                    api_instance = kubernetes.client.CoreV1Api(api_client)
                    return api_instance
                elif client == 'app':
                    app_instance = kubernetes.client.AppsV1Api(api_client)
                    return app_instance
        except Exception as e:
            logger.error(f"Exception occurred while configuring kubernetes client with error: {e}")
            raise e

    def _get_kubectl_processor(self, zone: str, cluster: str, client: str = 'api'):
        api_instance = self._gke_get_api_instance(zone=zone, cluster=cluster, client=client)
        eks_host = api_instance.api_client.configuration.host
        token = api_instance.api_client.configuration.api_key.get('authorization')
        ssl_ca_cert_path = api_instance.api_client.configuration.ssl_ca_cert
        return KubectlProcessor(api_server=eks_host, token=token, ssl_ca_cert_path=ssl_ca_cert_path)

    def execute_kubectl_command(self, zone: str, cluster: str, command: str):
        try:
            commands = command.split('\n')
            kubectl_client = self._get_kubectl_processor(zone, cluster, 'api')
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
