import json
import requests

config_url = 'https://jenkins-ndg.westeurope.cloudapp.azure.com/envs.json'
ecr_data = {
    'us': {
        'ecr': '889362988214.dkr.ecr.us-east-1.amazonaws.com',
        'repo': 'mseb-pr-dgecbrb2c-usea1-ecr-code-php'
    },
    'eu': {
        'ecr': '889362988214.dkr.ecr.eu-west-1.amazonaws.com',
        'repo': 'mseb-pr-dgecbrb2c-euwe1-ecr-code-php'
    },
    'croc': {
        'ecr': 'registry.k8s.dg.nestcroc.int',
        'repo': 'code-php'
    }
}


def environments_list():
    """
    Call URL and retrieve env configuration
    :return: dict
    """
    r = requests.get(config_url)
    env_list = json.loads(r.text)['envs']
    env_dict = {}
    nr_apps = []

    for e in env_list:
        env_dict[e['prefix']] = {
            'name': e['name'],
            'kube_config': e['kube_config'],
            'prefix': e['prefix'],
            'ecr_url': ecr_data[e['region']]['ecr'],
            'ecr_repo': ecr_data[e['region']]['repo'],
            'nr_apps': e['nrApps'] if 'nrApps' in e.keys() else [],
            'is_prod': 'isProd' in e.keys() and e['isProd'] == 'true' and 'unreleased' not in e.keys()
        }
    return env_dict
