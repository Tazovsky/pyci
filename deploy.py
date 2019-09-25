#!/usr/bin/env python3

import argparse
import os
import json
from tempfile import mkstemp
from pyci.yaml import *
from pyci.shinyproxy import *
import subprocess

parser = argparse.ArgumentParser(description="Deployment script")

parser.add_argument("--image", default=False, required=True, help="Docker image")
parser.add_argument("--work-dir", default=False, required=True,
                    help="Dir containing all required files such as application.yml and deployment_config.json")
parser.add_argument("--deployment-dir", default="~/deployment", required=False,
                    help="Where to put deployment files")
parser.add_argument("--user", default=False, required=True, help="User from deployment json to be used")
parser.add_argument("--url", default="https://www.shinyproxy.io/downloads/shinyproxy-2.3.0.jar",
                    required=False, help="URL to ShinyProxy jar")
parser.add_argument("--config", default=False, required=True, help="Config json")
parser.add_argument("--app-id", default=False, required=True, help="App ID from application.yml")

args = parser.parse_args()


# set working dir
os.chdir(args.work_dir)

# required variables
jar_name = "shinyproxy.jar"
deploy_cmd = "nohup java -jar {0} &".format(jar_name).split()
yaml_path = "application.yml"
deployment_dir = args.deployment_dir
deployment_config_path = args.config
user = args.user
url = args.url
app_id = args.app_id
docker_image_fullname = args.image

if os.path.exists(yaml_path) is False:
    raise Exception("{0} does not exist.".format(yaml_path))

if os.path.exists(deployment_config_path) is False:
    raise Exception("{0} does not exist.".format(deployment_config_path))

# create custom yml file
# you can replace some application.yml's field on the fly, e.g.
# it can be useful in CI when new docker image is build
# and you want to deploy app 'ont the fly'
subprocess.Popen(['docker', 'pull', docker_image_fullname]).wait()

make_custom_yaml(yaml_path, "container-image", docker_image_fullname, yaml_path)

new_json = filter_json_by_user(user, deployment_config_path)

# update deployment json with custom docker image
new_json["ci"][0]["shinyproxy"][0]["container-image"] = docker_image_fullname

new_json_path = mkstemp()[1]

with open(new_json_path, "w") as f:
    json.dump(new_json, f)

# before deploying ShinProxy you can test if app successfully runs in container
# id is the id of app in application.yaml
run_docker_cmd_from_yaml(yaml_path, json_path=new_json_path, user=user, id=app_id)

# deploy ShinyProxy
output = deploy(json_path=new_json_path,
                yaml_path=yaml_path,
                deployment_dir=deployment_dir,
                deploy_cmd=deploy_cmd,
                url=url,
                jar_name=jar_name)
