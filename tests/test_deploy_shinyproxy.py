from tempfile import mkdtemp, mkstemp
import git
from pyci.shinyproxy import *
from pyci.utils import *
from pyci.yaml import *
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import atexit
import time
import json

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


    yaml_path = "application.yml"
    deployment_dir = os.path.join(dir_path, "deployed")

    if False:
        test_dir = "/Users/foltynsk/Projects/pyci/tests/data/testdata"
        json_path = os.path.join(test_dir, "test_deploy_config.json")

    jar_name = "shinyproxy.jar"
    output = deploy(json_path=json_path,
                    yaml_path=yaml_path,
                    deployment_dir=deployment_dir,
                    deploy_cmd="nohup java -jar {0} &".format(jar_name).split(),
                    url="https://www.shinyproxy.io/downloads/shinyproxy-2.0.5.jar",
                    jar_name=jar_name)

    assert isinstance(output["user1"]["process"].pid, int)
    assert isinstance(output["user2"]["process"].pid, int)

    def kill_processes():
        for nm in [k for k in output.keys()]:
            print("Killing process ID: {0}...".format(output[nm]["process"].pid))
            output[nm]["process"].kill()

    atexit.register(kill_processes)

    # run selenium server
    options = webdriver.ChromeOptions()
    # headless option is set to not to open browser window
    options.add_argument("headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    atexit.register(driver.close)

    # check if 1st instance is running
    driver.get('http://localhost:{0}'.format("8081"))
    time.sleep(5)

    # elem = driver.find_element_by_xpath("/html/body/div/div/form")
    elem = driver.find_element_by_class_name("form-signin")
    assert str(type(elem)) == "<class 'selenium.webdriver.remote.webelement.WebElement'>"

    # check if 2nd instance is running
    driver.get('http://localhost:{0}/login'.format("8082"))
    time.sleep(5)
    # elem = driver.find_element_by_xpath("/html/body/div/div/form")
    elem = driver.find_element_by_class_name("form-signin")
    assert str(type(elem)) == "<class 'selenium.webdriver.remote.webelement.WebElement'>"


def test_deploy_shinyproxy_filtered_user(shared_datadir):
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

    yaml_path = "application.yml"
    deployment_dir = os.path.join(dir_path, "deployed")

    # filter json by specific user
    new_json = filter_json_by_user("user2", json_path)
    new_json_path = mkstemp()[1]
    with open(new_json_path, "w") as f:
        json.dump(new_json, f)

    jar_name = "shinyproxy.jar"
    output = deploy(json_path=new_json_path,
                    yaml_path=yaml_path,
                    deployment_dir=deployment_dir,
                    deploy_cmd="nohup java -jar {0} &".format(jar_name).split(),
                    url="https://www.shinyproxy.io/downloads/shinyproxy-2.0.5.jar",
                    jar_name=jar_name)

    assert isinstance(output["user2"]["process"].pid, int)

    def kill_processes():
        for nm in [k for k in output.keys()]:
            print("Killing process ID: {0}...".format(output[nm]["process"].pid))
            output[nm]["process"].kill()

    atexit.register(kill_processes)

    # run selenium server
    options = webdriver.ChromeOptions()
    # headless option is set to not to open browser window
    options.add_argument("headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    atexit.register(driver.close)

    # check if 2nd instance is running
    driver.get('http://localhost:{0}/login'.format("8082"))
    time.sleep(5)
    # elem = driver.find_element_by_xpath("/html/body/div/div/form")
    elem = driver.find_element_by_class_name("form-signin")
    assert str(type(elem)) == "<class 'selenium.webdriver.remote.webelement.WebElement'>"

