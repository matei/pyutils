"""
Notify team about list of tickets.

Usage: python notify.py --env ENV --branch BRANCH --path path/to/list.txt
OR: cat path/tto/list.txt | python notify.py --env ENV --branch BRANCH
"""

import argparse
import json
import os
import requests
import sys
from print_utils import *


def notify_deploy_flow(branch, env, path):
    flow = 'https://prod-121.westus.logic.azure.com:443/workflows/511aa055f9654ee7b8ef444cf76c38e2/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=q1manlxTYVzF5lQvMrLs0IA-KHEvPZTCk5eIi28At8Y'
    content = ''
    if path and os.path.isfile(path):
        with open(path, 'r') as f:
            content = f.read()
    else:
        for line in sys.stdin:
            content += line
    if not content.strip():
        print_error('missing content...')
        exit(1)
    body = json.dumps({'tickets': content, 'branch': branch, 'env': env})
    print_status('Sending notification...')
    r = requests.post(flow, data=body, headers={"Content-Type": "application/json"})
    if 200 <= r.status_code <= 299:
        print_success('Done!')
    else:
        print_error(f'There was an error sending the request. Response code was {r.status_code}. Body was {r.text}')


def notify_deploy_push(branch, env):
    message = f'Deployed {branch} on env'
    token = 'aqyc8x8d7fwcav3nr87i2jche1a5rm'
    user = 'CcCVahS58U8NqN31TMxvX9gtPuvkdp'
    endpoint = 'https://api.pushover.net/1/messages.json'
    payload = json.dumps({'token': token, 'user': user, message: 'message'})
    r = requests.post(endpoint, data=payload, headers={'Content-Type': 'application/json'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Notify')
    parser.add_argument('--branch', help='Branch build was made from', required=True)
    parser.add_argument('--env', help='Env build was deployed to', required=True)
    parser.add_argument('--path', help='Path to txt file with tickets', required=False)
    args = parser.parse_args()
    notify_deploy_flow(args.branch, args.env, args.path)
