import os
import subprocess
import sys
import time
import yaml

from utils.op_exception import OpException
from utils.print_utils import *


def kubectl_until(env, command, callback, wait, retries, debug=False):
    while retries > 0:
        print_status(f'{retries} waits left')
        retries -= 1
        try:
            result = kubectl(env, command, debug=debug)
        except Exception:
            result = ''
        if callback(result):
            return True
        time.sleep(wait)
    return False


def kubectl_exec(env, pod, command, retries=0, container=None, debug=False):
    """
    Run kubectl exec -it ${pod} -- command
    :param debug:
    :param container:
    :param env:
    :param pod:
    :param command:
    :param retries:
    :return:
    """
    return kubectl(env, f'exec -i {pod} {f"-c {container}" if container is not None else ""} -- {command}', retries, debug=debug)


def kubectl(env, command, retries=0, debug=False):
    """
    Run kubectl command
    :param debug:
    :param retries:
    :param env:
    :param command:
    :return:
    """
    # print(f'Running: {kubectl_line(env, command)}')
    try:
        kubectl_command = kubectl_line(env, command)
        print_debug(f'Running: {kubectl_command}', debug)
        return subprocess.check_output(kubectl_command, shell=True).decode(sys.stdout.encoding).replace("\r", "").strip()
    except Exception as e:
        if retries > 0:
            return kubectl(env, command, retries - 1)
        else:
            raise e


def kubectl_line(env, command):
    """
    Get kubectl command line
    :param env:
    :param command:
    :return:
    """
    kubeconfig_path = os.path.join(os.path.expanduser("~"), ".kube", env['kube_config'])
    return kubectl_kline(kubeconfig_path, command)


def kubectl_k(kubeconfig_path, command, retries=0, debug=False):
    """
    Run kubectl command with passed kubeconfig file
    :param kubeconfig_path:
    :param command:
    :param retries:
    :param debug:
    :return:
    """
    try:
        kubectl_command = kubectl_kline(kubeconfig_path, command)
        print_debug(f'Running: {kubectl_command}', debug)
        return subprocess.check_output(kubectl_command, shell=True).decode(sys.stdout.encoding).replace("\r", "").strip()
    except Exception as e:
        if retries > 0:
            return kubectl_k(kubeconfig_path, command, retries-1)
        else:
            raise e


def kubectl_kline(kubeconfig_path, command):
    """
    Get kubectl command line using passed kubeconfig file
    :param kubeconfig_path:
    :param command:
    :return:
    """
    if not os.path.isfile(kubeconfig_path):
        raise OpException(f'Invalid kubeconfig {kubeconfig_path}')
    return f'kubectl --kubeconfig={kubeconfig_path} {command}'


def kubectl_multiline(env, command, retries=0, debug=False):
    """
    Run kubectl command that generates multiline output. Collect result in list and return
    :param env:
    :param command:
    :param retries:
    :param debug:
    :return:
    """
    try:
        kubectl_command = kubectl_line(env, command)
        print_debug(f'Running {kubectl_command}', debug)
        result = []
        pipe = subprocess.Popen(kubectl_command, shell=True, stdout=subprocess.PIPE)
        for line in pipe.stdout:
            result.append(line.decode(sys.stdout.encoding).replace("\r", "").strip())
        return result
    except Exception as e:
        if retries > 0:
            return kubectl_multiline(env, command, retries - 1)
        else:
            raise e


def edit_configmap_key(env, configmap, replace={}):
    """
    Replace values in configmap
    Configmap should be key: value rows, replace is a replacement dictionary with all keys to be replaced
    :param env:
    :param configmap:
    :param replace:
    :return:
    """
    should_update = False
    configmap_mf = yaml.load("\n".join(kubectl_multiline(env, f'get cm {configmap} -o yaml')))
    if 'data' in configmap_mf.keys():
        for key, value in replace.items():
            if key not in configmap_mf['data'].keys() or configmap_mf['data'][key] != value:
                configmap_mf['data'][key] = value
                should_update = True
    if should_update:
        manifest_path = f'/tmp/{configmap}-manifest.yaml'
        with open(manifest_path, 'w') as f:
            f.write(yaml.dump(configmap_mf))
        kubectl(env, f'replace -f {manifest_path}')
        os.remove(manifest_path)


def delete_pod_type(env, pod_type='cron', wait_for_restart=False, retries=10):
    """
    Delete pod of type
    :param retries:
    :param wait_for_restart:
    :param env:
    :param pod_type:
    :return:
    """
    pod = find_pod_type(env, pod_type=pod_type)
    if pod:
        delete_pod_line = kubectl(env, f'delete pod {pod}')
    if wait_for_restart:
        find_pod_type(env, pod_type, retries)


def find_pod_type(env, pod_type='cron', retries=0, raise_exception=True):
    """
    Find pod name for env of type pod_type
    :param retries:
    :param env:
    :param pod_type:
    :return:
    """
    command = f"{kubectl_line(env, 'get pods')} | grep {env['prefix']}- | grep {pod_type} | grep Running | head -1 | cut -d ' ' -f1"
    output = subprocess.check_output(command, shell=True).decode(sys.stdout.encoding).replace("\r", "")
    if env['prefix'] not in output:
        if retries > 0:
            time.sleep(3)
            return find_pod_type(env, pod_type, retries-1)
        else:
            if raise_exception:
                raise OpException(f'Could not find {pod_type} pod for {env["prefix"]}')
            else:
                return None
    return output.strip()


def get_env_vars_from_pod(env, pod, variables):
    """
    Retrieve value of environment variable from pod
    :param env:
    :param pod:
    :param variables:
    :return:
    """
    result = {}
    for env_line in kubectl_exec(env, pod, f'env | grep -E \'{"|".join(variables)}\'').split("\n"):
        if env_line and '=' in env_line:
            result[env_line.split('=')[0].strip()] = env_line.split('=')[1].strip()
    return result


def change_cron_status(env, status=0):
    """
    Update run status of cron pod on env (0 = stop / 1 = start)
    :param env:
    :param status:
    :return:
    """
    print_status(f'Changing status of cron pod on {env["prefix"]} to {status}')
    kubectl(env, f'scale deployments/{env["prefix"]}-cron-php --replicas {status}')


def enable_maintenance(env, zero=True):
    """
    Enable maintenance page on env
    :param env:
    :return:
    """
    varnish_pod = find_pod_type(env, 'varnish')
    print_status(f'Enabling maintenance page on {env["prefix"]}')
    maintenance = 'maintenance'
    if zero:
        maintenance = 'maintenance-zero'
    kubectl_exec(env, varnish_pod, f'reload-config {maintenance}')
    print_success(f'Enabled maintenance page on {env["prefix"]}')


def disable_maintenance(env):
    """
    Disable maintenance page on env
    :param env:
    :return:
    """
    varnish_pod = find_pod_type(env, 'varnish')
    print_status(f'Disabling maintenance page on {env["prefix"]}')
    kubectl_exec(env, varnish_pod, f'reload-config varnish')
    print_success(f'Disabled maintenance page on {env["prefix"]}')


def recycle_php_pods(env, pod_type=None):
    """
    Recycle
    :param env:
    :return:
    """
    print_status(f'Recycling PHP pods for {env["prefix"]}')
    awk = 'awk \'{print $1}\''
    pod_type_filter = f"| grep {pod_type}" if pod_type is not None else ""
    get_pods_command = f'get pods | grep {env["prefix"]} | grep php {pod_type_filter} | {awk} | xargs'
    kubectl(env, f'delete pods $({kubectl_line(env, get_pods_command)}) --force=true --grace-period=0')
