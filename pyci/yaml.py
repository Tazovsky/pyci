from tempfile import mkstemp
from shutil import move
from os import fdopen, remove, path
import re
import json

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



def insert_json_in_yaml(json_path: str, yaml_path: str, output_path: str) -> dict:

    ### assert here ###

    json_dict = json.load(open(json_path, "r"))
    user_per_config = dict()

    for i in range(0, len(json_dict["ci"])):
        user = json_dict["ci"][i]["user"]
        val = json_dict["ci"][i]["shinyproxy"]
        user_per_config[user] = val


    for user in user_per_config:
        # iterate over fields to update in yaml
        print("Processing user: " + user)

        fh, tmp_path = mkstemp()

        field_x_value = user_per_config[user][0]
        for nm in field_x_value:
            print(str(nm) + ": " + str(field_x_value[nm]))
            # insert value into yaml
            # TODO: vectorize make_custom_yaml
            make_custom_yaml(yaml_path, str(nm), str(field_x_value[nm]), tmp_path)

        # Remove original file
        if path.isfile(output_path):
            remove(output_path)

        # Move new file
        move(tmp_path, output_path)