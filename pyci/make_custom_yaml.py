from tempfile import mkstemp
from shutil import move
from os import fdopen, remove, path
import re

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