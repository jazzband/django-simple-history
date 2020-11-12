from setuptools import setup

with open("README.rst") as readme, open("CHANGES.rst") as changes:
    setup(
        name="django-simple-history",
        use_scm_version={"version_scheme": "post-release"},
        setup_requires=["setuptools_scm"],
        description="Store model history and view/revert changes from admin site.",
        long_description="\n".join((readme.read(), changes.read())),
        author="Corey Bertram",
        author_email="corey@qr7.com",
        maintainer="Trey Hunner",
        url="https://github.com/jazzband/django-simple-history",
        packages=[
            "simple_history",
            "simple_history.management",
            "simple_history.management.commands",
            "simple_history.templatetags",
        ],
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Framework :: Django",
            "Environment :: Web Environment",
            "Intended Audience :: Developers",
            "Framework :: Django",
            "Framework :: Django :: 2.2",
            "Framework :: Django :: 3.0",
            "Framework :: Django :: 3.1",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "License :: OSI Approved :: BSD License",
        ],
        python_requires=">=3.5",
        include_package_data=True,
    )
