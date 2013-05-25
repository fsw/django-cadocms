
from fabric.api import env
from .deploy import Command as DeployCommand

env.use_ssh_config = True
env.host_string = django_settings.CADO_PROJECT + '_test'

class Command(DeployCommand):
    pass