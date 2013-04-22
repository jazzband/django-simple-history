from setuptools import setup, find_packages

template_patterns = [
    'templates/*.html',
    'templates/*/*.html',
    'templates/*/*/*.html',
]

packages = find_packages()

package_data = dict(
    (package_name, template_patterns)
    for package_name in packages
)

setup(
    name='django-simple-history',
    version='1.2.2',
    description='Store model history and view/revert changes from admin site.',
    long_description='\n'.join((
        open('README.rst').read(),
        open('CHANGES.rst').read(),
    )),
    author='Corey Bertram',
    author_email='corey@qr7.com',
    mantainer='Trey Hunner',
    url='https://github.com/treyhunner/django-simple-history',
    packages=packages,
    package_data=package_data,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: BSD License",
    ],
    tests_require=["Django>=1.3", "webtest", "django-webtest"],
    test_suite='runtests.main',
)
