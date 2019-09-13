# pyci

`pyci` is `python` wrapper to easily deploy multiple instances ShinyProxy apps
depending on config declared in `json` file.


## usage

In `json` can be declared any field from `application.yml` supported by 
`ShinyProxy` (see: https://www.shinyproxy.io/configuration/). Example `json`:

```json
{
   "ci":[
         {
            "user": "master",
            "shinyproxy":[{
              "port": 8080,
              "display-name": "Some app - prd",
              "port-range-start": 20000,
              "port-range-max": 20100,
              "container-volumes": "['/home/project/data:/data', '/home/project/data/config:/data/config']",
              "container-cmd": "['R', '-e shiny::runApp(\",/data/myapp/inst/shiny\")']"
            }]

         },
         {
            "user": "user@somemail.com",
            "shinyproxy":[{
              "port": 8080,
              "display-name": "Some app",
              "port-range-start": 20101,
              "port-range-max": 20200,
              "container-volumes": "['/home/project/data:/data', '/home/project/data/config:/data/config']",
              "container-cmd": "['R', '-e shiny::runApp(\"/data/myapp/inst/shiny\")']"
            }]

         }
      ]
}
```

Example deployment code:

```python
import os
import json
from tempfile import mkstemp
from pyci.yaml import *
from pyci.shinyproxy import *

new_json = filter_json_by_user("user@somemail.com", "ci/deployment_config.json")

new_json_path = mkstemp()[1]

with open(new_json_path, "w") as f:
    json.dump(new_json, f)

# required variables
jar_name = "shinyproxy.jar"
deploy_cmd="nohup java -jar {0} &".format(jar_name).split()
yaml_path =  "application.yml"

# create custom yml file
# you can replace some application.yml's field on the fly, e.g.
# it can be useful in CI when new docker image is build 
# and you want to deploy app 'ont the fly'  
docker_image_fullname = "some-new-docker-image-to-be-inserted-to-new-yaml"
make_custom_yaml(yaml_path, "container-image", docker_image_fullname, yaml_path)

# before deploying ShinProxy you can test if app successfully runs in container
# id is the id of app in application.yaml
run_docker_cmd_from_yaml(yaml_path, json_path = new_json_path user = "<git email or branch name, e.g. develop">, id = "01_hello")

# deploy ShinyProxy
output = deploy(json_path=new_json_path,
                yaml_path=yaml_path,
                deployment_dir="location-where-to-put-jar-file-and-application-yml",
                deploy_cmd=deploy_cmd,
                url="https://www.shinyproxy.io/downloads/shinyproxy-2.0.5.jar",
                jar_name=jar_name)


```