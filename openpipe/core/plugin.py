from dinterpol import Template
from sys import stderr
from os import environ, sep
from traceback import print_exc
from pprint import pformat
from os.path import join, dirname
from importlib import import_module
from glob import glob

ODP_RUNTIME_DEBUG = environ.get('ODP_RUNTIME_DEBUG')


class PluginRuntimeCore(object):

    def __init__(self, params=None):
        self.initial_params = params
        self.params_template = Template(params)
        self.failed_count = 0
        self.reference_count = 0
        self.init()

    def _on_input(self, item):
        try:
            if item is not None:
                self.params = self.params_template.render(item)
        except:  # NOQA: E722
            print("ITEM:\n" + pformat(item), file=stderr)
            print_exc(file=stderr)
            msg = (
                    "---------- Plugin %s dynamic params resolution failed ----------" % self.plugin_label)
            print(msg, file=stderr)
            #  raise(
            self.failed_count += 1
            exit(1)
        if item is None:
            self.reference_count -= 1
            if self.reference_count == 0:
                on_finish_func = getattr(self, 'on_finish', None)
                if on_finish_func:
                    if ODP_RUNTIME_DEBUG:
                        print("on_finish %s " % self.plugin_label)
                    on_finish_func(True)
                self.put(item)
        else:
            try:
                if ODP_RUNTIME_DEBUG:
                    print("on_item %s: %s" % (self.plugin_label, item))
                self.on_input(item)
            except SystemExit:
                exit(1)
            except:  # NOQA: E722
                self._execution_error(item)
            finally:
                if self.failed_count != 0:
                    exit(1)

    def _execution_error(self, item):
        print("ITEM:\n"+pformat(item), file=stderr)
        print_exc(file=stderr)
        msg = (
            "---------- Plugin %s execution failed ----------, item content:"
            % (self.plugin_label))
        print(msg, file=stderr)
        self.failed_count += 1

    def extend(self, plugin_path, extension_path):
        """ Extend plugin by importing modules from extension path """
        location = join(dirname(plugin_path), extension_path)
        sub_modules = glob(join(location, "*.py"))
        for filename in sub_modules:
            filename = '.'.join(filename.split(sep)[-6:])
            filename = filename.rsplit('.', 1)[0]
            import_module(filename)
