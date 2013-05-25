
from fabric.api import env
from .deploy import Command as DeployCommand
from django.conf import settings as django_settings

env.use_ssh_config = True
env.host_string = django_settings.CADO_PROJECT_GROUP + '_test'

class Command(DeployCommand):
    pass