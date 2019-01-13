import filecmp
from tempfile import mkstemp
from pyci.yaml import *
import json
from os.path import join as path

test_dir = "tests/data/testdata"
ref_dir = "tests/data/refdata"

def test_make_custom_yaml(shared_datadir):

    h1, yml1 = mkstemp()
    ref_yml1 = shared_datadir / "testdata/application.yml"

    make_custom_yaml(ref_yml1, "container-cmd", '["R", "-e print(1)"]', yml1)

    assert filecmp.cmp(shared_datadir / "refdata/application1.yml", yml1) is True

    h2, yml2 = mkstemp()
    ref_yml2 = shared_datadir / "refdata/application1.yml"

    make_custom_yaml(ref_yml2, "port", "8888", yml2)

    assert filecmp.cmp(shared_datadir / "refdata/application2.yml", yml2) is True

# to recreate ref objects
if False:
    make_custom_yaml(path(test_dir, "application.yml"), "container-cmd", '["R", "-e print(1)"]', path(ref_dir, "application1.yml"))
    make_custom_yaml(path(ref_dir, "application1.yml"), "port", "8888", path(ref_dir, "application2.yml"))


def test_insert_json_in_yaml(shared_datadir):

    json_path = shared_datadir / "testdata/config.json"
    yaml_path = shared_datadir / "testdata/application.yml"

    res = insert_json_in_yaml(json_path, yaml_path)

    # users validation
    assert [k for k in res.keys()] == ['master', 'user@somemail.com']

    # check if all needed fields are under users
    assert [k for k in res['master'].keys()] == ['json', 'yaml']
    assert [k for k in res['user@somemail.com'].keys()] == ['json', 'yaml']

    # field values validation
    assert res["user@somemail.com"]["json"][0]["port-range-max"] == 20200

    # load reference config
    with(open(shared_datadir / "refdata/config.json", "r")) as f:
        ref_res = json.loads(f.read())

    assert res == ref_res

def test_filter_json_by_user(shared_datadir):
    json_path = shared_datadir / "testdata/config.json"
    json_dict = json.load(open(json_path, "r"))

    assert filter_json_by_user("master", json_path)["ci"][0]["user"] == json_dict["ci"][0]["user"]
    assert filter_json_by_user("user@somemail.com", json_path)["ci"][0]["user"] == json_dict["ci"][1]["user"]

if False:
    with(open(path(ref_dir, "config.json"), "w")) as f:
        json.dump(res, f)
