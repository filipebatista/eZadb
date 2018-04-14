import pypandoc
from os import path

here = path.abspath(path.dirname(__file__))
with open('docs/README.rst', 'w') as fout:
    fout.write(pypandoc.convert('docs/README.md', 'rst'))
