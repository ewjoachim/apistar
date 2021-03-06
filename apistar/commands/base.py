from apistar.exceptions import ConfigurationError
import apistar
import click
import os
import pytest
import shutil
import sys
from wsgiref.simple_server import make_server


ROOT_DIR = os.path.dirname(apistar.__file__)
PROJECT_TEMPLATES_DIR = os.path.join(ROOT_DIR, 'project_templates')
PROJECT_TEMPLATE_CHOICES = os.listdir(PROJECT_TEMPLATES_DIR)


@click.command(help='Create a new project in TARGET_DIR.')
@click.argument('target_dir', default='')
@click.option('--template', type=click.Choice(PROJECT_TEMPLATE_CHOICES), default='standard', help='Select the project template to use.')
@click.option('-f', '--force', is_flag=True, help='Overwrite any existing project files.')
def new(target_dir, template, force):
    source_dir = os.path.join(PROJECT_TEMPLATES_DIR, template)

    copy_paths = []
    for dir_path, dirs, filenames in os.walk(source_dir):
        for filename in filenames:
            source_path = os.path.join(dir_path, filename)
            rel_path = os.path.relpath(source_path, source_dir)
            target_path = os.path.join(target_dir, rel_path)
            if os.path.exists(target_path) and not force:
                click.echo('Project files already exist. Use `-f` to overwrite.')
                sys.exit(1)
            copy_paths.append((source_path, target_path))

    for source_path, target_path in copy_paths:
        click.echo(target_path)
        target_dir = os.path.dirname(target_path)
        if target_dir:
            os.makedirs(target_dir, exist_ok=True)
        shutil.copy(source_path, target_path)


@click.command(help='Run the current app.')
@click.option('--host', '-h', default='localhost', type=str, help='The host of the webserver.')
@click.option('--port', '-p', default=8080, type=int, help='The port of the webserver.')
def run(host, port):
    from apistar.main import get_current_app
    app = get_current_app()

    try:
        click.echo('Running at http://{host}:{port}/'.format(host=host, port=port))
        make_server(host, port, app.wsgi).serve_forever()
    except KeyboardInterrupt:
        pass


@click.command(help='Run the test suite.')
@click.argument('file_or_dir', nargs=-1)
def test(file_or_dir):
    from apistar.main import get_current_app
    app = get_current_app()

    if not file_or_dir:
        file_or_dir = []
        if os.path.exists('tests'):
            file_or_dir.append('tests')
        if os.path.exists('tests.py'):
            file_or_dir.append('tests.py')
        if not file_or_dir:
            raise ConfigurationError("No 'tests/' directory or 'tests.py' module.")

    exitcode = pytest.main(list(file_or_dir))
    if exitcode:
        sys.exit(exitcode)
