import requests
import json
from login_test import login

projects_url = 'http://localhost:5000/projects_list'
project_name = 'shit'

def get_projects_list(token):
    headers = {'token': token}
    r = requests.get(projects_url, headers=headers)
    return json.loads(r.content)


def add_projects_list(token, project_name):
    headers = {'token': token}
    data = {'project_name': project_name}
    r = requests.post(projects_url, headers=headers, data=data)
    assert json.loads(r.content)['status'] == 'success'


def delete_projects_list(token, project_name):
    headers = {'token': token}
    data = {'project_name': project_name}
    r = requests.delete(projects_url, headers=headers, data=data)
    assert json.loads(r.content)['status'] == 'success'

if __name__ == '__main__':
    login = login()
    token = login['token']

    proj_list = get_projects_list(token)

    print proj_list

    add_projects_list(token, project_name)
    prev = get_projects_list(token)
    print prev

    delete_projects_list(token, project_name)
    curr = get_projects_list(token)
    print curr

    assert len(prev) == len(curr) + 1
