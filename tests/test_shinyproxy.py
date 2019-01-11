from tempfile import mkdtemp
import os
import hashlib
from pyci.shinyproxy import deploy

def test_deploy(shared_datadir):
    json_path = shared_datadir / "testdata/config.json"
    yaml_path = shared_datadir / "testdata/application.yml"
    deployment_dir = mkdtemp()

    output = deploy(json_path=json_path,
                    yaml_path=yaml_path,
                    deployment_dir=deployment_dir,
                    deploy_cmd=None,
                    url="https://www.shinyproxy.io/downloads/shinyproxy-2.0.5.jar",
                    jar_name="shinyproxy.jar")

    assert os.listdir(output["master"]["full_deployment_path"]) == ['application.yml', 'shinyproxy.jar']
    assert os.listdir(output["user@somemail.com"]["full_deployment_path"]) == ['application.yml', 'shinyproxy.jar']

    # check files hashes
    with(open(os.path.join(output["master"]["full_deployment_path"], "application.yml"), "r")) as f:
        f = f.read()

    assert hashlib.md5(f.encode("utf-8")).hexdigest() == 'ec9ce72f8f4a1641173d6dcbff863050'

    with(open(os.path.join(output["user@somemail.com"]["full_deployment_path"], "application.yml"), "r")) as f:
        f = f.read()

    assert hashlib.md5(f.encode("utf-8")).hexdigest() == '98753b036e2b06b2e161e0b2ad8db657'

def run_bash(shared_datadir):
    assert run_bash("echo 'test msg'").decode() == 'test msg\n'
    script_path = shared_datadir / "testdata/test_run_bash.sh  "
    result = run_bash(script_path)
    assert result.decode() == 'SUCCESS\n'
