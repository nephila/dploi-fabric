# -*- coding: utf-8 -*-
import os

import dploi_fabric
from django.conf import settings
from django.template import Template, Engine
from django.template.context import Context

if not settings.configured:
    settings.configure(DEBUG=True)


def render_template(path, context, strip_newlines=False):
    if not isinstance(context, Context):
        context = Context(context)
    with open(path) as template_file:
        template_data = template_file.read()

        if strip_newlines:
            template_data = ' '.join(template_data.splitlines())
        template = Template(template_data, engine=Engine())
    return template.render(context).lstrip()


def app_package_path(path):
    """
    returns the abs path with the dploi_fabric package as base
    """
    return os.path.abspath(os.path.join(os.path.dirname(dploi_fabric.__file__), path))
