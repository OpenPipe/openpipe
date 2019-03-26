from dinterpol import Template
from sys import stderr
from os import environ, sep
from traceback import print_exc
from pprint import pformat
from os.path import join, dirname
from importlib import import_module
from glob import glob

DEBUG = environ.get("DEBUG")


class PluginRuntimeBase:
    def __init__(self, config=None):
        self._tag = None
        self.initial_config = config
        self.config_template = Template(config)
        self.failed_count = 0
        self.reference_count = 0
        self.init()

    def _on_input(self, item, tag_item):
        if DEBUG:
            print(
                "on_input %s: \n\tInput: %s\n\tTag: %s"
                % (self.plugin_label, item, tag_item)
            )
        if item is not None:
            self._tag = tag_item
            try:
                self.config = self.config_template.render(item, tag_item)
            except:  # NOQA: E722
                if isinstance(item, bytes) and len(item) > 256:
                    item = item[:255]
                print("ITEM:\n" + pformat(item), file=stderr)
                if tag_item:
                    print("TAG ITEM:\n" + pformat(tag_item), file=stderr)
                print_exc(file=stderr)
                msg = (
                    "---------- Plugin %s dynamic config resolution failed ----------"
                    % self.plugin_label
                )
                print(msg, file=stderr)
                #  raise(
                self.failed_count += 1
                exit(1)

        if item is None:
            self.reference_count -= 1
            if self.reference_count == 0:
                on_finish_func = getattr(self, "on_finish", None)
                if on_finish_func:
                    if DEBUG:
                        print("on_finish %s [Tag: %s]" % (self.plugin_label, self._tag))
                    on_finish_func(True)
                self.put(item)
        else:
            try:
                self.on_input(item)
            except SystemExit:
                exit(1)
            except:  # NOQA: E722
                self._execution_error(item)
            finally:
                if self.failed_count != 0:
                    exit(1)

    def _execution_error(self, item):
        if isinstance(item, bytes) and len(item) > 256:
            item = item[:255]
        print("ITEM:\n" + pformat(item), file=stderr)
        if self._tag:
            print("TAG ITEM:\n" + pformat(self._tag), file=stderr)
        print_exc(file=stderr)
        msg = "---------- Plugin %s execution failed ----------, item content:" % (
            self.plugin_label
        )
        print(msg, file=stderr)
        self.failed_count += 1

    def extend(self, plugin_path, extension_path):
        """ Extend plugin by importing modules from extension path """
        location = join(dirname(plugin_path), extension_path)
        sub_modules = glob(join(location, "*.py"))
        for filename in sub_modules:
            filename = ".".join(filename.split(sep)[-6:])
            filename = filename.rsplit(".", 1)[0]
            import_module(filename)


class PluginRuntime(PluginRuntimeBase):
    def init(self):
        self.next_action = None

    def put(self, item):

        # Put on next
        if self.next_action:
            self.next_action._on_input(item, self._tag)

    def put_target(self, item, target):
        target._on_input(item, self._tag)

    def set_tag(self, tag_item):
        if DEBUG:
            print("set_tag %s : " % self.plugin_label, tag_item)
        self._tag = tag_item
