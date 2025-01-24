import os

from pydantic import BaseModel

from src.constants import DEFAULT_FILE_PERMISSIONS
from src.utils.helpers.path import find_project_root


class FolderConfig(BaseModel):
    permissions: str = DEFAULT_FILE_PERMISSIONS
    exist_ok: bool = True


class Folder:
    @staticmethod
    def create(path, config: FolderConfig = FolderConfig()):
        """Create a folder if it does not exist.

        Args:
            path (str): Path to the folder to be created.

        """
        try:
            cache_dir = os.path.join((find_project_root()), path)
        except ValueError:
            cache_dir = os.path.join(os.getcwd(), path)
        os.makedirs(cache_dir, mode=config.permissions, exist_ok=config.exist_ok)
