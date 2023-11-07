import os
from dotenv import load_dotenv

class ScriptEnvLoader:
    """
    A class to load environment variables from a .env file that matches the name of the running script.
    """

    @staticmethod
    def load_env(script_name: str):
        """
        Load environment variables from a .env file based on the provided script name.

        Args:
            script_name (str): The filename of the script.
        """
        env_file_name = os.path.splitext(script_name)[0] + '.env'

        if os.path.exists(env_file_name):
            load_dotenv(env_file_name)
            print(f"Environment variables loaded from {env_file_name}")
        else:
            print(f"No .env file found for {script_name}")
