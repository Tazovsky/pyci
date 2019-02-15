from tempfile import mkstemp
from shutil import move, copy
from os import fdopen, remove, path
import re
import json
import yaml
import subprocess
from subprocess import Popen, PIPE, DEVNULL
from threading import Timer
import atexit

# TODO: change print to INFO logger message

def make_custom_yaml(file_path: str, pattern: str, subst: str, output_path: str) -> None:

    #Create temp file
    fh, tmp_path = mkstemp()

    with fdopen(fh, 'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                #new_file.write(line.replace(pattern, subst))
                if bool(re.search("\s+" + pattern + ":", line)):
                    # get number of trailing spaces
                    spaces = re.search("\s+", line)
                    leading_spaces = spaces.group(0)
                    # combine new field
                    new_line = leading_spaces + pattern + ": " + subst
                    print("Replacing line: {0} with line: {1}\n".format(line, new_line))
                    new_file.write(new_line + "\n")
                else:
                    new_file.write(line)

    #Remove original file
    if path.isfile(output_path):
        remove(output_path)

    #Move new file
    move(tmp_path, output_path)

# output_path = 'tests/data/output.yml'
# yaml_path = 'tests/data/testdata/application.yml'
# json_path = 'tests/data/testdata/config.json'


def insert_json_in_yaml(json_path: str, yaml_path: str) -> dict:

    ### TODO: assert here ###

    json_dict = json.load(open(json_path, "r"))
    user_per_config = dict()

    for i in range(0, len(json_dict["ci"])):
        user = json_dict["ci"][i]["user"]
        val = json_dict["ci"][i]["shinyproxy"]
        user_per_config[user] = dict()
        user_per_config[user]["json"] = val


    for user in user_per_config:
        # iterate over fields to update in yaml
        print("Processing user: " + user)

        fh, new_yaml = mkstemp()

        # all updates in yaml will be written to new_yaml which is copy of origin yaml
        copy(yaml_path, new_yaml)

        field_x_value = user_per_config[user]["json"][0]
        for nm in field_x_value:
            print(str(nm) + ": " + str(field_x_value[nm]))
            # insert value into yaml
            make_custom_yaml(new_yaml, str(nm), str(field_x_value[nm]), new_yaml)

        # read new yaml into dict element
        with open(new_yaml, "r") as f:
            user_per_config[user]["yaml"] = f.read()

    return dict(user_per_config)

def filter_json_by_user(user: str, json_path: str):
    json_dict = json.load(open(json_path, "r"))
    filtered_json=dict(ci=[dict()])
    for i in range(len(json_dict["ci"])):
        if json_dict["ci"][i]["user"] == user:
            filtered_json["ci"] = [json_dict["ci"][i]]
            return filtered_json

    if filtered_json["ci"][0] == {}:
        raise Exception("User {0} not found".format(user))

if False:
    yaml_path = "tests/data/testdata/shinyproxy_example/application.yml"
    id = "06_tabsets"
    timeout_sec: int = 10
    docker_command = "R -e 'shinyproxy::run_06_tabsets()'"
    ######
    yaml_path = "dev/application.yml"
    json_path = "dev/deployment_config_new.json"
    id = "spendworx"


def run_docker_cmd_from_yaml(yaml_path: str,
                             json_path: str = None,
                             user: str = None,
                             id: str = "myapp",
                             docker_command: str = None,
                             timeout_sec: int = 10,
                             cont_name: str = "pycitest") -> object:

    if json_path is not None:
        if user is not str:
            raise Exception("'user' must be a string when providing 'json_path'")
        # insert_json_in_yaml returns dict with structure:
        # yaml_dict[user_name]['json'] or yaml_dict[user_name]['yaml']
        # second element is yaml saved as string so it needs to be converted to yaml file first and then read as dict
        res = insert_json_in_yaml(json_path, yaml_path)
        tmp_yaml_path = mkstemp()[1]
        yaml_content = res[user]["yaml"]
        with open(tmp_yaml_path, "w") as f:
            f.write(yaml_content)
        # read yaml
        with open(tmp_yaml_path, 'rt') as f:
            yaml_dict = yaml.safe_load(f.read())
    else:
        with open(yaml_path, 'rt') as f:
            yaml_dict = yaml.safe_load(f.read())

    specs = yaml_dict['proxy']['specs']
    app_specs = None
    for i in range(len(specs)):
        if specs[i]['id'] == id:
            app_specs = specs[i]
            break

    if app_specs is None:
        raise Exception("Element with ID = '{0}' hasn't been found in '{1}'".format(id, yaml_path))

    # ---------------------- create docker command
    img = app_specs["container-image"]

    if docker_command is None and 'container-cmd' in app_specs.keys():
        cmd = app_specs['container-cmd']
    else:
        cmd = docker_command

    if isinstance(cmd, list) is False:
        raise Exception("Command '{0} is not  list".format(str(cmd)))

    if "container-volumes" in app_specs.keys():
        vol = " ".join(["-v " + s for s in app_specs['container-volumes']]).split()

    else:
        vol = ""

    docker_cmd = [k for k in ['docker', 'run', '--rm', '--name', cont_name, '-i', vol, img] if k != '']
    docker_cmd = make_list_flat(docker_cmd)
    docker_cmd.extend(cmd)

    # cleanup at exit and before running container
    stop_and_remove_container(cont_name)

    print("\n>>> Running command:\n    {0}\n".format(str(" ".join(docker_cmd))))
    print("\n>>> Running command (shell form):\n    {0}\n".format(str(docker_cmd)))

    # --------------------- run container

    proc = Popen(docker_cmd, stdout=PIPE, stderr=PIPE, shell=False)

    timer = Timer(timeout_sec, proc.kill)
    try:
        timer.start()
        stdout, stderr = proc.communicate()
    finally:
        timer.cancel()
        # cleanup after running container
        stop_and_remove_container(cont_name)

    # because timer.cancel does SIGTERM which has -9 exit code
    if proc.returncode != -9 and stderr:
        proc.kill()
        raise Exception("Error: " + str(stderr))
    else:
        print("Successfully run Shiny app")

    return proc

def stop_and_remove_container(cont_name) -> None:
    try:
        proc = Popen(['docker', 'stop', cont_name], stdout=PIPE, stderr=PIPE, shell=False)
        stdout, stderr = proc.communicate()
    finally:
        if stderr:
            print("No container to stop")

    try:
        proc = Popen(['docker', 'rm', '-f', cont_name], stdout=PIPE, stderr=PIPE, shell=False)
        stdout, stderr = proc.communicate()
    finally:
        if stderr:
            print("No container to remove")

def make_list_flat(l):
    flist = []
    flist.extend([l]) if (type(l) is not list) else [flist.extend(make_list_flat(e)) for e in l]
    return flist
