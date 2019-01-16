import pkg_resources
import yaml
import os
import logging.config
print(">>>>>>>>>>>>> before setup_logging")

path = pkg_resources.resource_filename('pyci', 'data')
with open(os.path.join(path, 'logging.yaml'), 'rt') as f:
    config = yaml.safe_load(f.read())
logging.config.dictConfig(config)

if __name__ == '__main__':
    path = pkg_resources.resource_filename('pyci', 'data')
    with open(os.path.join(path, 'logging.yaml'), 'rt') as f:
        config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

