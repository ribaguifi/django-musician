import os

from setuptools import find_packages, setup


# Dynamically calculate the version
version = __import__('musician').get_version()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


setup(
    name="django-musician",
    version=version,
    url='https://gitlab.pangea.org/slamora/django-musician.git',
    author='Santiago Lamora',
    author_email='santiago@ribaguifi.com',
    description=('Client of the django-orchestra web hosting control panel '
                 'for the final users.'),
    #long_description='TODO',
    #license = 'AGPLv3 License',
    packages=find_packages(),
    include_package_data = True,
    zip_safe=False,
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.1',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
)
