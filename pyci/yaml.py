from tempfile import mkstemp
from shutil import move, copy
from os import fdopen, remove, path
import re
import json
import yaml
import subprocess
from subprocess import Popen, PIPE, DEVNULL
from threading import Timer

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
                    print("Replacing line: {0}\nwith line: {1}".format(line, new_line))
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

def run_docker_cmd_from_yaml(yaml_path: str, id: str = "spendworx", timeout_sec: int = 10) -> object:
    with open(yaml_path, 'rt') as f:
        yaml_dict = yaml.safe_load(f.read())
    specs = yaml_dict['proxy']['specs']
    app_specs = None
    for i in range(len(specs)):
        if specs[i]['id'] == id:
            app_specs = specs[i]

    if app_specs is None:
        raise Exception("Element with ID = '{0}' hasn't been found in '{1}'".format(id, yaml_path))

    cmd = " ".join(app_specs['container-cmd'])
    vol = " ".join(["-v " + s for s in app_specs['container-volumes']])
    img = app_specs['container-image']
    docker_cmd = "docker run {0} -i {1} bash -c \"{2}\"".format(vol, img, cmd)

    proc = Popen(docker_cmd.split(), stdout=PIPE, stderr=PIPE)
    timer = Timer(timeout_sec, proc.kill)
    try:
        timer.start()
        stdout, stderr = proc.communicate()
    finally:
        timer.cancel()

    if stderr:
        raise Exception("Error: " + str(stderr))

    return proc
