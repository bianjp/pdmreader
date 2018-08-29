from os import path
from setuptools import setup

import pdmreader

root_dir = path.abspath(path.dirname(__file__))
with open(path.join(root_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="pdmreader",
    version=pdmreader.__version__,

    url='https://github.com/bianjp/pdmreader',
    author='Bian Jiaping',
    author_email='ssbianjp@gmail.com',
    license='MIT',
    keywords='pdm',
    description='Interactive reader for PowerDesigner PDM files',
    long_description_content_type='text/markdown',
    long_description=long_description,

    packages=['pdmreader'],
    include_package_data=True,
    zip_safe=True,

    python_requires='>= 3.7',

    entry_points={
        'console_scripts': [
            'pdmreader = pdmreader.main:main',
        ]
    },

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
    ],

)
