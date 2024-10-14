#!/usr/bin/python3
"""Module for HTML template rendering with dynamic content"""
import os
from jinja2 import Template


def html_template_render(template_name, **context):
    """Create HTML string based on template and context"""
    template_path = os.path.join(
        'api', 'v1', 'templates', f'{template_names}.html'
    )
    html_rendered = ''
    if os.path.isfile(template_path):
        frontend_domain = os.getenv('FRONTEND_DOMAIN')
        context['frontend_domain'] = frontend_domain
        with open(template_path) as file:
            doc = Template(file.read())
            html_rendered = doc.render(**context)
    return html_rendered
