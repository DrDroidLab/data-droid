import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from client.api_processors.api.api_processor_facade import api_processor_facade
from client.api_processors.api.api_processor import ApiSource


def run_bash_command(command):
    # Get the registered bash API processor
    bash_processor = api_processor_facade.get_source_api_processor(ApiSource.BASH)

    # Execute the bash command
    result = bash_processor.execute_http_get_api(command)

    # Print the result
    print("Command Output:")
    print("STDOUT:", result["stdout"])
    print("STDERR:", result["stderr"])
    print("Return Code:", result["returncode"])


if __name__ == "__main__":
    command = 'df -h'
    run_bash_command(command)
