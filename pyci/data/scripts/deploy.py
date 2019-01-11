from pyci.shinyproxy import *

jar_name = "shinyproxy.jar"

deploy(json_path="config.json",
       yaml_path="application.yml",
       deployment_dir="deployed",
       url="https://www.shinyproxy.io/downloads/shinyproxy-2.0.5.jar",
       jar_name=jar_name,
       deploy_cmd="nohup java -jar {0} &".format(jar_name))


deploy_cmd = "nohup java -jar {0} &".format(jar_name)
deploy_cmd.split()

deploy_cmd.split()
p = subprocess.Popen(["java", "-jar shinyproxy.jar'"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT);