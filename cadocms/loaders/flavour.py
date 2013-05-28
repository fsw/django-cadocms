import os
from django.template import TemplateDoesNotExist
from django.template.loader import find_template_loader, BaseLoader
from django.conf import settings

from cadocms.middleware import get_current_request 

class Loader(BaseLoader):
    is_usable = True
    
    def __init__(self, *args, **kwargs):
        loaders = []
        for loader_name in settings.TEMPLATE_LOADERS:
            if loader_name != 'cadocms.loaders.flavour.Loader':
                loader = find_template_loader(loader_name)
                if loader is not None:
                    loaders.append(loader)
        self.loaders = tuple(loaders)
        super(BaseLoader, self).__init__(*args, **kwargs)
    
    def load_template(self, template_name, template_dirs=None):
        request = get_current_request()
        for loader in self.loaders:
            for suffix in ['.' + request.flavour, '']:
                try:
                    name, extension = os.path.splitext(template_name)
                    return loader(name + suffix + extension, template_dirs)
                except TemplateDoesNotExist:
                    pass
        raise TemplateDoesNotExist("Tried %s" % template_name)
    """
    def load_template_source(self, template_name, template_dirs=None):
        template_name = self.prepare_template_name(template_name)
        for loader in self.template_source_loaders:
            if hasattr(loader, 'load_template_source'):
                try:
                    return loader.load_template_source(template_name, template_dirs)
                except TemplateDoesNotExist:
                    pass
        raise TemplateDoesNotExist("Tried %s" % template_name)
        """