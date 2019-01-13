from tempfile import mkdtemp
import git
from pyci.shinyproxy import *
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import atexit

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

    atexit.register(output["user1"]["process"].kill)
    atexit.register(output["user2"]["process"].kill)

    # run selenium server
    options = webdriver.ChromeOptions()
    # headless option is set to not to open browser window
    options.add_argument("headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    atexit.register(driver.close)

    # check if 1st instance is running
    driver.get('http://localhost:{0}/login'.format("8081"))
    # elem = driver.find_element_by_xpath("/html/body/div/div/form")
    elem = driver.find_element_by_class_name("form-signin")
    assert str(type(elem)) == "<class 'selenium.webdriver.remote.webelement.WebElement'>"

    # check if 2nd instance is running
    driver.get('http://localhost:{0}/login'.format("8082"))
    # elem = driver.find_element_by_xpath("/html/body/div/div/form")
    elem = driver.find_element_by_class_name("form-signin")
    assert str(type(elem)) == "<class 'selenium.webdriver.remote.webelement.WebElement'>"


