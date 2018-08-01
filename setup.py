from setuptools import setup
import simple_history

tests_require = [
    'Django>=1.11', 'WebTest==2.0.24', 'django-webtest==1.8.0', 'mock==1.0.1']

setup(
    name='django-simple-history',
    version=simple_history.__version__,
    description='Store model history and view/revert changes from admin site.',
    long_description='\n'.join((
        open('README.rst').read(),
        open('CHANGES.rst').read(),
    )),
    author='Corey Bertram',
    author_email='corey@qr7.com',
    maintainer='Trey Hunner',
    url='https://github.com/treyhunner/django-simple-history',
    packages=[
        'simple_history', 'simple_history.management',
        'simple_history.management.commands', 'simple_history.templatetags'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Framework :: Django",
        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        "License :: OSI Approved :: BSD License",
    ],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    tests_require=tests_require,
    include_package_data=True,
    test_suite='runtests.main',
)
