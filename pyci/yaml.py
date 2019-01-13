from tempfile import mkstemp
from shutil import move, copy
from os import fdopen, remove, path
import re
import json

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

json_path = '/Users/foltynsk/Projects/pyci/tests/data/testdata/config.json'

def filter_json_by_user(user: str, json_path: str):
    json_dict = json.load(open(json_path, "r"))
    filtered_json=dict(ci=[dict()])
    for i in range(len(json_dict["ci"])):
        if json_dict["ci"][i]["user"] == user:
            filtered_json["ci"][0] = json_dict["ci"][i]
            return filtered_json

    if filtered_json["ci"][0] == {}:
        raise Exception("User {0} not found".format(user))
