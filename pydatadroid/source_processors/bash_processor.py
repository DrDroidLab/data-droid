import io
import logging
import subprocess
from abc import ABC

import paramiko as paramiko
from google.protobuf.wrappers_pb2 import StringValue

from pydatadroid.protos.result_pb2 import BashCommandOutputResult, ResultType, Result
from pydatadroid.source_processors.processor import Processor
from pydatadroid.utils.proto_utils import proto_to_dict

logger = logging.getLogger(__name__)


class BashProcessor(Processor, ABC):

    def __init__(self, remote_server: str, pem_passphrase: str = None, pem_str: str = None, pem_path: str = None):
        self.remote_user = remote_server.split("@")[0]
        self.remote_host = remote_server.split("@")[1]
        self.pem_passphrase = pem_passphrase
        self.pem = None
        if pem_path:
            with open(pem_path, 'r') as pem_file:
                self.pem = pem_file.read().strip()
        elif pem_str:
            self.pem = pem_str.strip()

    def get_connection(self):
        try:
            if self.remote_host and self.remote_user and self.pem:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                    if self.pem_passphrase:
                        key = paramiko.RSAKey.from_private_key(io.StringIO(self.pem),
                                                               password=self.pem_passphrase)
                    else:
                        key = paramiko.RSAKey.from_private_key(io.StringIO(self.pem))
                    client.connect(hostname=self.remote_host, username=self.remote_user, pkey=key)
                except Exception as e:
                    try:
                        if self.pem_passphrase:
                            key = paramiko.Ed25519Key.from_private_key(io.StringIO(self.pem),
                                                                       password=self.pem_passphrase)
                        else:
                            key = paramiko.Ed25519Key.from_private_key(io.StringIO(self.pem))
                        client.connect(hostname=self.remote_host, username=self.remote_user, pkey=key)
                    except Exception as e:
                        try:
                            if self.pem_passphrase:
                                key = paramiko.ECDSAKey.from_private_key(
                                    io.StringIO(self.pem), password=self.pem_passphrase)
                            else:
                                key = paramiko.ECDSAKey.from_private_key(io.StringIO(self.pem))
                            client.connect(hostname=self.remote_host, username=self.remote_user, pkey=key)
                        except Exception as e:
                            try:
                                if self.pem_passphrase:
                                    key = paramiko.DSSKey.from_private_key(
                                        io.StringIO(self.pem), password=self.pem_passphrase)
                                else:
                                    key = paramiko.DSSKey.from_private_key(io.StringIO(self.pem))
                                client.connect(hostname=self.remote_host, username=self.remote_user, pkey=key)
                            except Exception as e:
                                logger.error(f"Exception occurred while creating remote connection with error: {e}")
                                raise e

            elif self.remote_host and self.pem_passphrase:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(hostname=self.remote_host, username=self.remote_user, password=self.pem_passphrase)
            elif self.remote_host and self.remote_user:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(hostname=self.remote_host, username=self.remote_user)
            else:
                client = None
            return client
        except Exception as e:
            logger.error(f"Exception occurred while creating remote connection with error: {e}")
            raise e

    def test_connection(self):
        try:
            command = 'echo "Connection successful"'
            client = self.get_connection()
            if client:
                try:
                    stdin, stdout, stderr = client.exec_command(command)
                    output = stdout.read().decode('utf-8')
                    if output.strip() == "Connection successful":
                        return True
                    else:
                        raise Exception("Connection failed")
                except paramiko.AuthenticationException as e:
                    logger.error(f"Authentication error: {str(e)}")
                    raise e
                except paramiko.SSHException as e:
                    logger.error(f"SSH connection error: {str(e)}")
                    raise e
                except Exception as e:
                    logger.error(f"Error: {str(e)}")
                    raise e
                finally:
                    client.close()
            else:
                try:
                    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE, universal_newlines=True)
                    return True if result.stdout.strip() == "Connection successful" else False
                except subprocess.CalledProcessError as e:
                    logger.error(f"Error executing command{command}: {e}")
                    raise e
        except Exception as e:
            logger.error(f"Exception occurred while creating remote connection with error: {e}")
            raise e

    def execute_commands(self, commands: [str]):
        try:
            client = self.get_connection()
            try:
                outputs = {}
                for command in commands:
                    command = command.strip()
                    try:
                        stdin, stdout, stderr = client.exec_command(command)
                        output = stdout.read().decode('utf-8')
                        outputs[command] = output.strip()
                    except paramiko.AuthenticationException as e:
                        logger.error(f"Authentication error: {str(e)}")
                        outputs[command] = str(e)
                        continue
                    except paramiko.SSHException as e:
                        logger.error(f"SSH connection error: {str(e)}")
                        outputs[command] = str(e)
                        continue
                    except Exception as e:
                        logger.error(f"Error: {str(e)}")
                        outputs[command] = str(e)
                        continue
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
            except Exception as e:
                logger.error(f"Error: {str(e)}")
                raise e
            finally:
                client.close()
        except Exception as e:
            logger.error(f"Exception occurred while executing remote command with error: {e}")
            raise e
