import pkg_resources
import shutil
import os

data_path = pkg_resources.resource_filename('pyci', 'data/')

def get_deploy_py(dest: str = ".") -> None:

    shutil.copy(os.path.join(data_path, "scripts", "deploy.py"), dest)