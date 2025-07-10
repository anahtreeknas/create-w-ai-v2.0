import requests
import json
from typing import Optional
from pydantic import TypeAdapter
from sarvam_datatypes import resource_id_from_name
from sarvam_agents_sdk import LanguageName, ChannelType, LLMModelVariant, AppStatus, App, V2VApp
from sarvam_datatypes import get_ist_datetime



org_id = "sarvamai"
workspace_id = "default"

def get_token():
    url = "https://apps-qa.sarvam.ai/api/auth/login"
    payload = {
    "org_id": "sarvamai",
    "user_id": "admin",
    "password": "leading-chamois"
    }
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    token = response.json()
    token = "Bearer " + token["access_token"]
    return token


def update_app(app_name, app_id, app_config):
    # app_id = resource_id_from_name(app_name)
    headers = {
        "authorization": get_token(),   
        "content-type": "application/json",
    }

    update_url = f"https://apps-qa.sarvam.ai/api/app-authoring/orgs/{org_id}/workspaces/{workspace_id}/apps/{app_id}"
    app_config = create_app_config(app_config, app_name, app_id)
    payload = {"app": app_config, "app_name": app_name}
    response = requests.put(update_url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def create_app(app_name, app_config=None):
    headers = {
        "authorization": get_token(),
        "content-type": "application/json",
    }
    
    create_url = f"https://apps-qa.sarvam.ai/api/app-authoring/orgs/{org_id}/workspaces/{workspace_id}/apps"
    
    app_id = resource_id_from_name(app_name)
    payload = {"app_name": app_name}

    print("app_config", app_config)
    
    if app_config is not None:
        app_config = create_app_config(app_config, app_name, app_id)
        payload["app"] = app_config
    
    response = requests.post(create_url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def create_app_config(generated_app_config, app_name, app_id):

    intro_message_config = {}
    intro_message_config["audio"] = generated_app_config["intro_message"]
    model_variant = LLMModelVariant.TOTA_V6.value
    print("type(generated_app_config)", type(generated_app_config))
    agent_config = generated_app_config["agent_config"]
    agent_config["enable_structured_prompt"] = True

    app_json = {
            "language_config": {
                "initial_language_name": LanguageName.HINDI.value,
                "supported_languages": [LanguageName.HINDI.value],
            },
            "llm_config": {
                "llm_model_variant": model_variant,
                "agent_config": agent_config,
            },
            "intro_message_config": intro_message_config,
            "channel_type": "v2v",
        }
    # print("App attributes:")
    # print(f"App.__dict__: {App.__dict__}")
    # print(f"App.__annotations__: {App.__annotations__}")
    # print(f"App.__fields__: {App.__fields__}")
    # print(f"App.model_fields: {App.model_fields}")

    
    try:
        app = V2VApp(
            **app_json,
        )
        return app.model_dump(mode="json")
    except Exception as e:
        import traceback
        print("Full error traceback:")
        print(traceback.format_exc())
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"app_json keys: {list(app_json.keys())}")
        print(f"app_json content: {app_json}")
        raise

    
    
    









    




