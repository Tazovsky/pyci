import filecmp
from tempfile import mkstemp
from pyci.yaml import make_custom_yaml
from os.path import join as path
import os

def test_make_custom_yaml():

    print(">>>>>> wd:" + str(os.path.dirname(os.path.realpath(__file__))))
    print("os.getcwd(): " + os.getcwd())

    data_dir_path = "data"

    h1, yml1 = mkstemp()
    ref_yml1 = path(data_dir_path, "testdata/application.yml")

    print(os.listdir(path(data_dir_path, "testdata/")))

    make_custom_yaml(ref_yml1, "container-cmd", '["R", "-e print(1)"]', yml1)

    assert filecmp.cmp(path(data_dir_path, "refdata/application1.yml"), yml1) == True


    h2, yml2 = mkstemp()
    ref_yml2 = path(data_dir_path, "refdata/application1.yml")

    print(os.listdir(ref_yml2))

    make_custom_yaml(ref_yml2, "port", "8888", yml2)

    assert filecmp.cmp(path(data_dir_path, "refdata/application2.yml"), yml2) == True

# to recreate ref objects
if False:
    make_custom_yaml("tests/data/testdata/application.yml", "container-cmd", '["R", "-e print(1)"]', "tests/data/refdata/application1.yml")
    make_custom_yaml("tests/data/refdata/application1.yml", "port", "8888", "tests/data/refdata/application2.yml")