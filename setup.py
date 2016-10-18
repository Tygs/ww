
import re
import sys
import setuptools


def get_version(path="src/ww/__init__.py"):
    """ Return the version of by with regex intead of importing it"""
    init_content = open(path, "rt").read()
    pattern = r"^__version__ = ['\"]([^'\"]*)['\"]"
    return re.search(pattern, init_content, re.M).group(1)


def get_requirements(path):

    setuppy_format = \
        'https://github.com/{user}/{repo}/tarball/master#egg={egg}'

    setuppy_pattern = \
        r'github.com/(?P<user>[^/.]+)/(?P<repo>[^.]+).git#egg=(?P<egg>.+)'

    dep_links = []
    install_requires = []
    with open(path) as f:
        for line in f:

            if line.startswith('-e'):
                url_infos = re.search(setuppy_pattern, line).groupdict()
                dep_links.append(setuppy_format.format(**url_infos))
                egg_name = '=='.join(url_infos['egg'].rsplit('-', 1))
                install_requires.append(egg_name)
            else:
                install_requires.append(line.strip())

    return install_requires, dep_links


requirements, dep_links = get_requirements('requirements.txt')
dev_requirements, dev_dep_links = get_requirements('dev-requirements.txt')

if sys.version_info.major == 2:
    dev_requirements.remove('mypy-lang')

setuptools.setup(
    name='ww',
    version=get_version(),
    description="Wrappers for Python builtins with higher-level APIs",
    long_description=open('README.rst').read().strip(),
    author="Sam et Max",
    author_email="lesametlemax@gmail.com",
    url='https://github.com/tygs/ww/',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    install_requires=requirements,
    extras_require={
        'dev': dev_requirements
    },
    setup_requires=['pytest-runner'],
    tests_require=dev_requirements,
    include_package_data=True,
    license='MIT',
    zip_safe=False,
    keywords='ww',
    classifiers=['Development Status :: 1 - Planning',
                 'Intended Audience :: Developers',
                 'Natural Language :: English',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Operating System :: OS Independent'],
)
