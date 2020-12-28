import requests

def create_clickup_task(task_title, list_id, token):
    response = requests.post(
        f'https://api.clickup.com/api/v2/list/{list_id}/task/',
        json={
            'name': task_title,
        },
        headers={
            'Authorization': token
        },
    )
