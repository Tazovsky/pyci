import urllib.request as request
import shutil
import ssl
import os
import warnings

def get_jar(url: str = "https://www.shinyproxy.io/downloads/shinyproxy-2.0.5.jar",
            target_file: str = "./{0}".format(url.split("/")[-1])) -> str:

    dir_name = os.path.dirname(target_file)

    if dir_name not in ["", ".", "~"] and os.path.isdir(dir_name) == False:
        os.makedirs(dir_name)
        warnings.warn("Created directory: " + dir_name)

    # see: https://stackoverflow.com/a/28052583/5002478
    context = ssl._create_unverified_context()

    with request.urlopen(url, context = context) as response, open(target_file, 'wb') as target_file:
        shutil.copyfileobj(response, target_file)

    return target_file
