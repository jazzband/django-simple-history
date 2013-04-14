from setuptools import setup, find_packages


setup(name='django-simple-history',
      version='1.1.3.post1',
      description='Store Django model history with the ability to revert back to a specific change at any time.',
      author='Corey Bertram',
      author_email='corey@qr7.com',
      mantainer='Trey Hunner',
      url='https://github.com/treyhunner/django-simple-history',
      packages=find_packages(),
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Framework :: Django",
          ],
    tests_require=["Django>=1.2"],
    test_suite='runtests.main',
)
