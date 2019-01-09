import filecmp
from tempfile import mkstemp
from pyci import make_custom_yaml


def test_output_yml():

    h1, yml1 = mkstemp()
    ref_yml1 = "testdata/application.yml"
    make_custom_yaml(ref_yml1, "container-cmd", '["R", "-e print(1)"]', yml1)

    assert filecmp.cmp("refdata/application1.yml", yml1) == True


    h2, yml2 = mkstemp()
    ref_yml2 = "refdata/application1.yml"
    make_custom_yaml(ref_yml2, "port", "8888", yml2)

    assert filecmp.cmp("refdata/application2.yml", yml2) == True

# to recreate ref objects
if False:
    make_custom_yaml("tests/data/testdata/application.yml", "container-cmd", '["R", "-e print(1)"]', "tests/data/refdata/application1.yml")
    make_custom_yaml("tests/data/refdata/application1.yml", "port", "8888", "tests/data/refdata/application2.yml")