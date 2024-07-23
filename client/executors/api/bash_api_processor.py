import subprocess
from .api_processor import ApiProcessor, ApiSource


class BashApiProcessor(ApiProcessor):
    source = ApiSource.BASH
    configured = True  # Set to True if no additional configuration is needed

    def execute_http_get_api(self, command, headers=None, params=None):
        try:
            result = subprocess.run(command, shell=True, check=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    universal_newlines=True)
            return {
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "returncode": result.returncode
            }
        except subprocess.CalledProcessError as e:
            return {
                "error": f"Command execution failed: {e}",
                "stdout": e.stdout.strip() if e.stdout else "",
                "stderr": e.stderr.strip() if e.stderr else "",
                "returncode": e.returncode
            }
