import filecmp
from tempfile import mkstemp
from pyci.yaml import make_custom_yaml
from os.path import join as path
import os

def test_make_custom_yaml(shared_datadir):

    print(">>>>>> wd:" + str(os.path.dirname(os.path.realpath(__file__))))
    print("os.getcwd(): " + os.getcwd())

    h1, yml1 = mkstemp()
    ref_yml1 = shared_datadir / "testdata/application.yml"

    make_custom_yaml(ref_yml1, "container-cmd", '["R", "-e print(1)"]', yml1)

    assert filecmp.cmp(shared_datadir / "refdata/application1.yml", yml1) == True

    h2, yml2 = mkstemp()
    ref_yml2 = shared_datadir / "refdata/application1.yml"

    make_custom_yaml(ref_yml2, "port", "8888", yml2)

    assert filecmp.cmp(shared_datadir / "refdata/application2.yml", yml2) == True

# to recreate ref objects
if False:
    make_custom_yaml("tests/data/testdata/application.yml", "container-cmd", '["R", "-e print(1)"]', "tests/data/refdata/application1.yml")
    make_custom_yaml("tests/data/refdata/application1.yml", "port", "8888", "tests/data/refdata/application2.yml")