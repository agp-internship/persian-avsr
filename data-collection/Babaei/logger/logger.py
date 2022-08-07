import logging.config
import yaml

def logger_config(config_path='logger/logger-conf.yml'):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)