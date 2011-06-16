from setuptools import setup, find_packages

setup(
    name='lmsh',
    version='0.1',
    description="Command line interface to Lab Manager SOAP API",
    license='BSD',
    author='James Saryerwinnie',
    author_email='jlsnpi@gmail.com',
    packages=find_packages(),
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

