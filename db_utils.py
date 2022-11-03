from utils.kube import *
from utils.op_exception import OpException
from utils.print_utils import *
import base64
import json
import threading


class MysqlProxy(threading.Thread):
    """
    Proxy Mysql connection over kubectl tunnel
    """
    def __init__(self, env, local_port=3307):
        threading.Thread.__init__(self)
        self.env = env
        self.local_port = local_port

    def run(self):
        proxy_pod = find_pod_type(self.env, 'haproxy-mysql')
        if proxy_pod:
            print_status(f'Opening up tunnel to {self.env["prefix"]}')
            try:
                kubectl(self.env, f'port-forward svc/{self.env["prefix"]}-haproxy-mysql {self.local_port}:3306')
            except subprocess.CalledProcessError:
                print_status(f'{self.env["prefix"]} proxy connection closed')
        else:
            raise OpException(f'Could not find proxy pod for {self.env["prefix"]}')


def get_mysql_credentials(env, from_secret = True):
    if from_secret:
        return get_mysql_credentials_from_secret(env)
    backend_pod = find_pod_type(env, 'backend')
    if 'backend' not in backend_pod:
        raise OpException(f'Could not find backend pod for {env["prefix"]}')
    print_status(f'Retrieving DB credentials from {backend_pod}')
    output = kubectl(env, f'exec -i {backend_pod} -- cat app/etc/env.php | grep -A4 indexer | tail -4').replace("'", '')
    creds = {}
    output = "\n".join(
        [line[:-1] for line in output.split("\n")]
    )
    for k, v in [line.strip().split('=>') for line in output.split("\n") if line.strip()]:
        #print_debug(f'{k} is {v}')
        creds[k.strip()] = v.strip()
    return creds


def get_mysql_credentials_from_secret(env):
    secret_name = f'{env["prefix"]}-magento-secret'
    secret_content = json.loads(kubectl(env, f'get secret {secret_name} -o json'))
    env_prefix_upper = env['prefix'].upper()
    return {
        'host': base64.b64decode(secret_content['data'][f'{env_prefix_upper}M2SETUPDBHOST']).decode(),
        'username': base64.b64decode(secret_content['data'][f'{env_prefix_upper}M2SETUPDBUSER']).decode(),
        'password': base64.b64decode(secret_content['data'][f'{env_prefix_upper}M2SETUPDBPASSWORD']).decode(),
        'dbname': base64.b64decode(secret_content['data'][f'{env_prefix_upper}M2SETUPDBNAME']).decode()
    }
