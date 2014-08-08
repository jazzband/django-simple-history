from setuptools import setup
import simple_history

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
    packages=["simple_history", "simple_history.management", "simple_history.management.commands"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        "License :: OSI Approved :: BSD License",
    ],
    tests_require=["Django>=1.4", "webtest==2.0.6", "django-webtest==1.7"],
    include_package_data=True,
    test_suite='runtests.main',
)
