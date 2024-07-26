import base64
import json
import logging
import subprocess
import tempfile
from abc import ABC
from google.protobuf.wrappers_pb2 import StringValue

from pydatadroid.protos.result_pb2 import BashCommandOutputResult, Result, ResultType
from pydatadroid.source_processors.processor import Processor
from pydatadroid.utils.proto_utils import proto_to_dict

logger = logging.getLogger(__name__)


class KubectlProcessor(Processor, ABC):
    client = None

    def __init__(self, api_server: str, token: str, ssl_ca_cert_data: str = None, ssl_ca_cert_path: str = None):
        self.__api_server = api_server
        self.__token = token
        self.__ca_cert = None
        if ssl_ca_cert_path:
            self.__ca_cert = ssl_ca_cert_path
        elif ssl_ca_cert_data:
            fp = tempfile.NamedTemporaryFile(delete=False)
            ca_filename = fp.name
            cert_bs = base64.urlsafe_b64decode(ssl_ca_cert_data.encode('utf-8'))
            fp.write(cert_bs)
            fp.close()
            self.__ca_cert = ca_filename

    def get_connection(self):
        try:
            if self.__ca_cert:
                kubectl_command = [
                    "kubectl",
                    f"--server={self.__api_server}",
                    f"--token={self.__token}",
                    f"--certificate-authority={self.__ca_cert}"
                ]
            else:
                kubectl_command = [
                    "kubectl",
                    f"--server={self.__api_server}",
                    f"--token={self.__token}",
                    f"--insecure-skip-tls-verify=true"
                ]
            return kubectl_command
        except Exception as e:
            logger.error(f"Exception occurred while creating kubectl client with error: {e}")
            raise e

    def test_connection(self):
        command = "kubectl version --output=json"
        if 'kubectl' in command:
            command = command.replace('kubectl', '')
        if self.__ca_cert:
            kubectl_command = [
                                  "kubectl",
                                  f"--server={self.__api_server}",
                                  f"--token={self.__token}",
                                  f"--certificate-authority={self.__ca_cert}"
                              ] + command.split()
        else:
            kubectl_command = [
                                  "kubectl",
                                  f"--server={self.__api_server}",
                                  f"--token={self.__token}",
                                  f"--insecure-skip-tls-verify=true"
                              ] + command.split()
        try:
            process = subprocess.Popen(kubectl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                kube_version = json.loads(stdout)
                if 'serverVersion' in kube_version:
                    return True
                elif stderr:
                    raise Exception(f"Failed to connect with kubernetes cluster. Error: {stderr}")
                else:
                    raise Exception("Failed to connect with kubernetes cluster. No server version information found in "
                                    "command: kubectl version --output=json")
            else:
                raise Exception(f"Failed to connect with kubernetes cluster. Error: {stderr}")
        except Exception as e:
            logger.error(f"Exception occurred while executing kubectl command with error: {e}")
            raise e

    def execute_command(self, command):
        command = command.strip()
        if 'kubectl' in command:
            command = command.replace('kubectl', '')
        commands = [cmd.strip() for cmd in command.split('|')]

        outputs = {}
        stdin_data = None

        for i, cmd in enumerate(commands):
            if self.__ca_cert:
                kubectl_command = [
                                      "kubectl",
                                      f"--server={self.__api_server}",
                                      f"--token={self.__token}",
                                      f"--certificate-authority={self.__ca_cert}"
                                  ] + cmd.split()
            else:
                kubectl_command = [
                                      "kubectl",
                                      f"--server={self.__api_server}",
                                      f"--token={self.__token}",
                                      f"--insecure-skip-tls-verify=true"
                                  ] + cmd.split()
            try:
                if i == 0:
                    process = subprocess.Popen(kubectl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                               text=True)
                else:
                    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE, text=True, shell=True)

                stdout, stderr = process.communicate(input=stdin_data)
                stdin_data = stdout

                if process.returncode == 0:
                    outputs[cmd] = stdout.strip()
                else:
                    outputs[cmd] = stderr.strip()

            except Exception as e:
                logger.error(f"Exception occurred while executing kubectl command with error: {e}")
                outputs[cmd] = str(e)

        command_output_protos = []
        for command, output in outputs.items():
            bash_command_result = BashCommandOutputResult.CommandOutput(
                command=StringValue(value=command),
                output=StringValue(value=output)
            )
            command_output_protos.append(bash_command_result)

        result_proto = Result(
            type=ResultType.BASH_COMMAND_OUTPUT,
            bash_command_output=BashCommandOutputResult(
                command_outputs=command_output_protos
            )
        )
        return proto_to_dict(result_proto)
