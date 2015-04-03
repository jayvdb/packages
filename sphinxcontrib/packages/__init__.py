# TODO Licence etc.

import collections
import os
import pkg_resources
import platform
import re
import subprocess

from docutils import nodes
from docutils.statemachine import StringList
from docutils.parsers.rst.directives import flag, unchanged
from sphinx.util.compat import Directive
from sphinx.util.nodes import nested_parse_with_titles
from docutils.parsers.rst import directives

def node_or_str(text):
    if isinstance(text, str):
        return nodes.paragraph(text=text)
    else:
        return text

def simple_link(text, target):
    container = nodes.paragraph()
    reference = nodes.reference("", "", internal=False, refuri=target)
    reference.append(nodes.paragraph(text=text))
    container.append(reference)
    return container


def simple_table(ncolumns, headers, body):
    def _build_table_row(data):
        row = nodes.row()
        for cell in data:
            entry = nodes.entry()
            row += entry
            entry.append(node_or_str(cell))
        return row

    table = nodes.table()
    tgroup = nodes.tgroup(cols=2)
    table += tgroup
    for colwidth in [10]*ncolumns:
        colspec = nodes.colspec(colwidth = colwidth)
        tgroup += colspec

    # HEAD
    thead = nodes.thead()
    tgroup += thead
    for row in [headers]:
        thead += _build_table_row(row)

    # BODY
    tbody = nodes.tbody()
    tgroup += tbody
    for row in body:
        tbody += _build_table_row(row)

    return table

def simple_bulletlist(items):
    return nodes.bullet_list("", *[nodes.list_item('', node_or_str(item)) for item in items])

class PlatformDirective(Directive):
    has_content = False

    def body(self):
        for attr in [
                "machine",
                "platform",
                "system",
                "release",
                "version",
                "processor",
                ]:
            yield [attr.replace("_", " ").capitalize(), str(getattr(platform, attr)())]

        for attr in [
                "architecture",
                "linux_distribution",
                ]:
            yield [attr.replace("_", " ").capitalize(), " ".join([str(item) for item in getattr(platform, attr)()])]

    def run(self):
        return [simple_table(
            2,
            [],
            self.body(),
            )]

class BinDirective(Directive):

    def dirs(self):
        for path in os.getenv("PATH").split(":"):
            binaries = []
            for binary in sorted(os.listdir(os.path.expanduser(os.path.expandvars(path)))):
                if os.path.isfile(os.path.join(path, binary)) and os.access(os.path.join(path, binary), os.X_OK):
                    binaries.append(binary)
            yield (path, binaries)

    def run(self):
        items = []
        for path, binaries in self.dirs():
            item = nodes.compound()
            item.append(nodes.literal(text=path))
            cells = []
            for binary in binaries:
                cells.append([nodes.paragraph(text=binary)])
            if cells:
                item.append(simple_table(
                    1,
                    [],
                    cells,
                    ))
            else:
                item.append(nodes.emphasis(text="empty"))
            items.append(item)
        return [simple_bulletlist(items)]

def deepdict_factory(depth):
    """TODO

    >>> d = deepdict_factory(2)()
    >>> type(d)
    <class 'collections.defaultdict'>
    >>> type(d[0])
    <class 'collections.defaultdict'>
    >>> type(d[0]["foo"])
    <class 'list'>
    """
    if depth == 0:
        return list
    else:
        def deep_dict():
            return collections.defaultdict(deepdict_factory(depth - 1))
        return deep_dict

class CmdDirective(Directive):
    regexp = ""
    command = []
    headers = {}
    sections = []

    def filter(self, match):
        return match

    def _iter_match(self, output):
        compiled_re = re.compile(self.regexp)
        for line in output:
            match = compiled_re.match(line.decode("utf8").strip())
            if match:
                processed_match = self.filter(match.groupdict())
                if processed_match is not None:
                    yield processed_match

    def _render_deepdict(self, deepdict):
        if type(deepdict) == list:
            items = dict()
            for item in deepdict:
                items[item[self.sortkey]] = [item[key] for key in self.headers]
            return simple_table(
                    len(self.headers),
                    self.headers.values(),
                    [items[key] for key in sorted(items.keys())],
                    )
        else:
            return TODO_RECURSIVE_LISTE_SORTED(deepdict)

    def run(self):
        try:
            process = subprocess.Popen(
                    self.command,
                    stdin=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    )
            deepdict = deepdict_factory(len(self.sections))()
            for match in self._iter_match(process.stdout):
                subdict = deepdict
                for section in self.sections:
                    subdict = subdict[section]
                subdict.append(match)
            process.wait()
        except Exception as exception:
            error = nodes.error()
            error.append(nodes.paragraph(text=str(exception)))
            return [error]

        return [self._render_deepdict(deepdict)]

class DebDirective(CmdDirective):

    regexp = r'\t'.join([r'(?P<{}>[^\t]*)'.format(key) for key in ['status', 'section', 'package', 'version', 'homepage', 'summary']])
    command = [
        "dpkg-query",
        "--show",
        "--showformat=${db:Status-Status}\t${Section}\t${binary:Package}\t${Version}\t${Homepage}\t${binary:Summary}\n",
        ]
    headers = collections.OrderedDict([
            ("package_node", "Package name"),
            ("version", "Version"),
            ("summary", "Summary"),
            ])
    sortkey = "package"
    #sections = ["section"] TODO

    def filter(self, match):
        if match['status'] == "installed":
            if match['homepage']:
                match['package_node'] = simple_link(text=match['package'], target=match['homepage'])
            else:
                match['package_node'] = match['package']
            return match
        else:
            return None

class PyDirective(CmdDirective):

    regexp = r'\t'.join([r'(?P<{}>[^\t]*)'.format(key) for key in ['package', 'version', 'path']])
    headers = collections.OrderedDict([
            ("package", "Package name"),
            ("version", "Version"),
            ])
    sortkey = "package"
    python = ""

    def filter(self, match):
        if match['path'].startswith(pkg_resources.resource_filename(__name__, "data")):
            return None
        return match

    @property
    def command(self):
        return [
            self.python,
            pkg_resources.resource_filename(
                __name__,
                os.path.join("data", "bin", "list_modules.py"),
                ),
            ]

class Py3Directive(PyDirective):
    python = "python3"

class Py2Directive(PyDirective):
    python = "python2"

class CDirective(CmdDirective):
    regexp = r'^ *(?P<library>[^ ]*) '
    headers = collections.OrderedDict([
            ("library", "Library"),
            ])
    command = ["/sbin/ldconfig", "-p"]
    sortkey = "library"

def setup(app):
    app.add_directive('packages:platform', PlatformDirective)
    app.add_directive('packages:bin', BinDirective)
    app.add_directive('packages:deb', DebDirective)
    app.add_directive('packages:python2', Py2Directive)
    app.add_directive('packages:python3', Py3Directive)
    app.add_directive('packages:c', CDirective)

