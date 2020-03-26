import os
import json
import logging
import requests

import azure.functions as func

GitHubToken = os.environ["GitHubToken"]

def main(event: func.EventGridEvent):
    result = json.dumps({
        'id': event.id,
        'data': event.get_json(),
        'topic': event.topic,
        'subject': event.subject,
        'event_type': event.event_type,
    })

    logging.info('Python EventGrid trigger processed an event: %s', result)

    data = event.get_json()

    logging.info(f'EventGrid Data: {json.dumps(data)}')

    if event.event_type == "Microsoft.MachineLearningServices.ModelRegistered":
        model = str(data["modelName"])
        if "seer" in model.lower():
            version = data["modelVersion"]
            ghSha = data["modelTags"]["github_ref"]
            ghUri = "https://api.github.com/repos/cloudscaleml/seer/dispatches"

            logging.info('Callin GitHub hook')
            response = seer_registered(GitHubToken, ghUri, model, version, ghSha)

            logging.info(f'GitHub Response: {response.status_code}, Text: {response.text}')


def seer_registered(token: str, uri: str, model: str, version: int, sha: str) -> requests.Response:
    headers = {
        "Accept": "application/vnd.github.everest-preview+json",
        "Authorization": f"token {token}"
    }
    data = {
        "event_type": "model-registered", 
        "client_payload": { 
            "model": model,
            "version": str(version),
            "service": f"{model}-svc",
            "compute_target": "sauron",
            "github_ref": sha,
            "workspace": "hal",
            "resource_group": "robots"
        }
    }
    return requests.post(uri, headers=headers, data=json.dumps(data))

