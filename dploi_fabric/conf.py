from deployment import settings, project_name
from fabric.api import env

env.project_name = project_name

for key, value in settings.items():
    value['identifier']=key


def load_settings(identifier):
    if not any(settings[identifier]['hosts']):
        raise RuntimeError("Hosts not defined, stopping...")
    env.identifier = identifier
    for key, value in settings[identifier].items():
        setattr(env, key, value)
