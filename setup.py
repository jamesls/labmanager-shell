import os
from setuptools import setup, find_packages


setup(
    name='lmsh',
    version='0.1.4',
    description="Command line interface to Lab Manager SOAP API",
    long_description=open(os.path.join(os.path.dirname(__file__),
                                       'README.rst')).read(),
    license='BSD',
    author='James Saryerwinnie',
    author_email='jlsnpi@gmail.com',
    packages=find_packages(),
    keywords="labmanager",
    url="https://github.com/jamesls/labmanager-shell",
    entry_points={
        'console_scripts': ['lmsh = labmanager.shell:main'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
    ],
    install_requires=[
        'suds',
        'argparse',
        'texttable',
    ]
)

