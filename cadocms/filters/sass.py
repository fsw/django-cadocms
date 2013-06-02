import re,os
from compressor.filters import CompilerFilter
from django.core.files.temp import NamedTemporaryFile
from django.conf import settings
from django.contrib.staticfiles import finders

class SassFilter(CompilerFilter):
    
    def __init__(self, content, attrs, filter_type=None, filename=None):
        self.attrs = attrs
        super(SassFilter, self).__init__(
                    content,
                    filter_type = filter_type,
                    command='sass --scss',
                    filename = filename)
    
    def replace_imports(self, parentpath, content, stack):
        #TODO: limit stac, check circular imports
        import_pattern = "@import \"(.*?)\";"
        imports = re.findall(import_pattern, content)
        for file in imports:
            if file.startswith('/'):
                filepath = file[1:]
            else:
                filepath = parentpath.replace(os.path.basename(parentpath), '') + file
            if finders.find(filepath):
                #print "@import \"%s\";" % file
                content = content.replace("@import \"%s\";" % file, 
                          self.replace_imports(filepath, open(finders.find(filepath), 'r').read(), stack))
        return content
    
    def input(self, **kwargs):
        #print self.content, self.filename, self.infile
        staticpath = self.attrs.get('href').replace(settings.STATIC_URL, '')
        self.content = self.replace_imports(staticpath, self.content, [])
        #print self.content
        return super(SassFilter, self).input(**kwargs)