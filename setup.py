from setuptools import setup, find_packages


setup(
    name='django-simple-history',
    version='1.3.0',
    description='Store model history and view/revert changes from admin site.',
    long_description='\n'.join((
        open('README.rst').read(),
        open('CHANGES.rst').read(),
    )),
    author='Corey Bertram',
    author_email='corey@qr7.com',
    maintainer='Trey Hunner',
    url='https://github.com/treyhunner/django-simple-history',
    packages=find_packages(),
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
    tests_require=["Django>=1.3", "webtest", "django-webtest"],
    include_package_data=True,
    test_suite='runtests.main',
)
