import urllib.request as request
import shutil
import ssl
import os
import warnings
import re
import subprocess
from subprocess import Popen, PIPE, DEVNULL

# import package module(s)
from pyci.yaml import insert_json_in_yaml
from pyci.utils import data_path

# helpers
if False:
    test_dir = "tests/data/testdata"
    json_path = os.path.join(test_dir, "config.json")
    yaml_path = os.path.join(test_dir, "application.yml")
    deployment_dir = "deployment"
    deploy_cmd = None
    url = "https://www.shinyproxy.io/downloads/shinyproxy-2.0.5.jar"
    jar_name = "shinyproxy.jar"


# TODO: change warnings to INFO logger message

def get_jar(url: str = "https://www.shinyproxy.io/downloads/shinyproxy-2.0.5.jar",
            target_file: str = "shinyproxy.jar") -> str:

    dir_name = os.path.dirname(target_file)

    if dir_name not in ["", ".", "~"] and os.path.isdir(dir_name) is False:
        os.makedirs(dir_name)
        warnings.warn("Created directory: " + dir_name)

    # see: https://stackoverflow.com/a/28052583/5002478
    context = ssl._create_unverified_context()

    with request.urlopen(url, context = context) as response, open(target_file, 'wb') as target_file:
        shutil.copyfileobj(response, target_file)

    return target_file


def run_bash(what: str = None):

    if what is None:
        return None
    elif type(what) is not list:
        raise Exception("'what' argument must be a list")

    session = subprocess.Popen(what, shell=False, stdout=PIPE, stderr=PIPE)

    if session.poll() is not None:
        stdout, stderr = session.communicate()
        if stderr:
            raise Exception("Error " + str(stderr))

    return session

def deploy(json_path: str,
           yaml_path: str,
           deployment_dir: str,
           deploy_cmd: str = None,
           url: str = "https://www.shinyproxy.io/downloads/shinyproxy-2.0.5.jar",
           jar_name: str = "shinyproxy.jar",
           pid_file: str = "process.pid",
           kill_process: bool = True) -> dict:

    ### assert ###
    if os.path.isfile(json_path) is False:
        raise Exception("Path '{0} does not exist'".format(json_path))

    if os.path.isfile(yaml_path) is False:
        raise Exception("Path '{0} does not exist'".format(yaml_path))

    # check if deployment location exists
    if os.path.isdir(deployment_dir) is False:
        os.makedirs(deployment_dir)
        warnings.warn("Created directory: " + deployment_dir)

    res = insert_json_in_yaml(json_path, yaml_path)

    # TODO: validate HERE if there are overlapping shinyproxy ports between users

    for user in res:
        print("Deploying user: " + user)
        user_dir = re.sub("[^a-zA-Z0-9]", "_", user)

        full_deployment_path = os.path.join(deployment_dir, user_dir)

        if os.path.isdir(full_deployment_path) is False:
            os.makedirs(full_deployment_path)

        print("Keys: {0}".format(res[user].keys()))

        yaml_content = res[user]["yaml"]

        deployed_yaml_path = os.path.join(full_deployment_path, "application.yml")
        print("Creating '{0}'".format(deployed_yaml_path))
        with open(deployed_yaml_path, "w") as f:
            f.write(yaml_content)

        # download shinyproxy jar file
        jar_path = os.path.join(full_deployment_path, jar_name)
        get_jar(url=url, target_file=jar_path)

        # copy bash script from template
        script_path = os.path.join(data_path, "scripts", "deploy.py")
        shutil.copy(script_path, full_deployment_path)

        # execute deployment command, e.g. systemctl service service_name start
        if deploy_cmd is not None:
            origin_wd=os.getcwd()
            # set WD to deployment path
            os.chdir(full_deployment_path)
            print("Deploying from location: {0}".format(os.getcwd()))
            # kill process if pid exists and still running
            if kill_process and os.path.isfile(pid_file):
                pid = open(pid_file, "r").read()
                subprocess.call(["kill {0}".format(pid)], shell=True)
                print("Removing PID file")
                os.remove(pid_file)
            print("Running cmd: {0}".format(deploy_cmd))
            deploy_cmd_output = run_bash(what=deploy_cmd)
            # write pid file
            with open(pid_file, "w") as f:
                f.write(str(deploy_cmd_output.pid))
            # back to origin working dir
            os.chdir(origin_wd)
            res[user].update(dict(process=deploy_cmd_output))

        # return dict containing detailed info
        res[user].update(dict(full_deployment_path=full_deployment_path))

    return dict(res)
