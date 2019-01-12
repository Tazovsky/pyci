from tempfile import mkdtemp
import git
import os
from pyci.shinyproxy import *
from pyci.utils import data_path

def test_deploy_shinyproxy(shared_datadir):
    # working dir
    dir_path = mkdtemp()
    # clone example repo
    example_repo = "https://github.com/openanalytics/shinyproxy-config-examples"
    example_dir = "01-standalone-docker-engine"
    git.Git(dir_path).clone(example_repo)
    # decalre vars
    json_path = shared_datadir / "testdata/test_deploy_config.json"
    # set working dir
    os.chdir(os.path.join(dir_path, "shinyproxy-config-examples", example_dir))


    yaml_path = "./application.yml"
    deployment_dir = os.path.join(dir_path, "deployed")
    url = "https://www.shinyproxy.io/downloads/shinyproxy-2.0.5.jar"
    jar_name = "shinyproxy.jar"

    if False:
        test_dir = "/Users/foltynsk/Projects/pyci/tests/data/testdata"
        json_path = os.path.join(test_dir, "test_deploy_config.json")
        json_dict = json.load(open(json_path, "r"))

    # os.getcwd()
    # '/Users/foltynsk/Projects/pyci'

    jar_name = "shinyproxy.jar"
    output = deploy(json_path=json_path,
                    yaml_path=yaml_path,
                    deployment_dir=deployment_dir,
                    deploy_cmd="nohup java -jar {0} &".format(jar_name),
                    url="https://www.shinyproxy.io/downloads/shinyproxy-2.0.5.jar",
                    jar_name=jar_name)



    os.listdir(os.path.join(deployment_dir, "user1"))
