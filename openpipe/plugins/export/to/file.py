"""
Export input content to file
"""
from openpipe.engine import PluginRuntime
from os.path import expanduser
import json


class Plugin(PluginRuntime):

    default_config = """
    path:                   # Filename of the file to create/overwrite/append
    content: $_$            # Content to be written to the file
    mode: "w"               # Open file mode (write/append)
    on item close: False    # Force file close after each received item
    """

    def on_start(self, config, segment_resolver):
        self.last_path = None
        self.file = None

    def on_input(self, item):
        path = self.config['path']
        path = expanduser(path)
        if path != self.last_path:
            if self.file:
                self.file.close()
            self.file = open(path, self.config['mode'])
            self.last_path = path
        content = self.config['content']
        if path.endswith('.json'):
            content = json.dumps(content, indent=4)
        self.file.write(content)
        if self.config['on item close']:
            self.file.close()
            self.file = None
            self.last_path = None
        self.put(item)

    def on_complete(self):
        if self.file:
            self.file.close()
