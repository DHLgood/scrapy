import os
import sys
import io
from setuptools import setup, find_packages

if sys.version_info[:2] < (3, 6):
    raise Exception('This version of dhl-scrap needs Python 3.6 or later.')


def readfile(fname):
    path = os.path.join(os.path.dirname(__file__), fname)
    return io.open(path, encoding='utf8').read()


REQUIRED_PACKAGES = [
    'scrapy >= 1.4.0',
    'ruamel.yaml >= 0.15.19',
    'bs4 >= 0.0.1',
    'boto3 >= 1.5.6',
]

EXTRA_PACKAGES = {
}

TEST_PACKAGES = [
    'pytest',
    'pylint'
]

package_data = {
    "dhl-scrap": ["opt/dhl/conf/*.yml"]
}


setup(
    name='dhl-scrap',
    version='0.1.0',
    description='dhl Web Scraping spiders',
    long_description=readfile('README.md'),
    ext_modules=[],
    packages=find_packages(),
    entry_points={
        'scrapy': 'settings = dhl_scrap.settings',
    },

    keywords='dhl, data, crawl, spider',
    platforms='any',
    zip_safe=False,

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: Other/Proprietary License',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    setup_requires=['pytest-runner', 'pytest-pylint'],
    install_requires=REQUIRED_PACKAGES,
    extras_require=EXTRA_PACKAGES,
    tests_require=TEST_PACKAGES,
    test_suite="tests",
    include_package_data=True
)
