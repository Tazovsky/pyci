import urllib.request as request
import shutil
import ssl
import os
import warnings
import re

# import package module(s)
from pyci.yaml import insert_json_in_yaml

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


test_dir = "tests/data/testdata"
json_path = os.path.join(test_dir, "config.json")
yaml_path = os.path.join(test_dir, "application.yml")
deployment_dir = "deployment"
deploy_cmd = None
url = "https://www.shinyproxy.io/downloads/shinyproxy-2.0.5.jar"
jar_name = "shinyproxy.jar"


def deploy(json_path: str, yaml_path: str, deployment_dir: str, deploy_cmd: None,
           url: str = "https://www.shinyproxy.io/downloads/shinyproxy-2.0.5.jar",
           jar_name: str = "shinyproxy.jar") -> None:

    ### assert ###
    if os.path.isfile(json_path) is False:
        raise Exception("Path '{0} does not exist'".format(json_path))

    if os.path.isfile(yaml_path) is False:
        raise Exception("Path '{0} does not exist'".format(yaml_path))

    # check if deployment location exists
    if os.path.isdir(deployment_dir) is False:
        os.makedirs(deployment_dir)
        warnings.warn("Created directory: " + deployment_dir)

    if deploy_cmd is not None and deploy_cmd is not str:
        raise Exception("'deploy_cmd' argument is not a string")

    res = insert_json_in_yaml(json_path, yaml_path)

    print("keys from res: {0}".format(res["user@somemail.com"].keys()))

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

        # execute deployment command, e.g. systemctl service service_name start
        if deploy_cmd is not None:
            os.system(deploy_cmd)


deploy(json_path=json_path, yaml_path=yaml_path, deployment_dir=deployment_dir,
       deploy_cmd=None,
       url="https://www.shinyproxy.io/downloads/shinyproxy-2.0.5.jar",
       jar_name="shinyproxy.jar")
