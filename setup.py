from os import path
from setuptools import setup, find_packages
from ezadb import __AUTHOR__
from ezadb import __version__

setup(
    name='eZadb',
    version=__version__,
    description='ezADB - Easy Android Debug Bridge. Use adb like a boss!',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python'
    ],
    long_description=open(path.join(path.abspath(path.dirname(__file__)),'docs/README.rst')).read(),
    keywords='android adb android-debug-bridge development',
    url='https://filipebatista.github.io/eZadb',
    author='{user1}'.format(user1=__AUTHOR__[0]['Name']),
    author_email='{email1}'.format(email1=__AUTHOR__[0]['Email']),
    license='GPL-3.0',
    packages=find_packages(),
    install_requires=[
        'backports.shutil_which',
        'configparser==3.5.0',
        'pygubu==0.9.8.1',
        'enum34==1.1.6',
        'pillow==4.3.0',
        'future'
    ],
    entry_points={
        'console_scripts': [
            'ezadb_cmd = ezadb.ezadb_cmd:main'
        ],
        'gui_scripts': [
            'ezadb = ezadb.__main__:start_ezadb'
        ]
    },
    include_package_data=True,
    python_requires='>=2.7',
    zip_safe=False)
