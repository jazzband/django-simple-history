from setuptools import setup

with open("README.rst") as readme, open("CHANGES.rst") as changes:
    setup(
        name="django-simple-history",
        use_scm_version={
            "version_scheme": "post-release",
            "local_scheme": "node-and-date",
            "relative_to": __file__,
            "root": ".",
            "fallback_version": "0.0.0",
        },
        setup_requires=["setuptools_scm"],
        # DEV: Remove `asgiref` when the minimum required Django version is 4.2
        install_requires=["asgiref>=3.6"],
        description="Store model history and view/revert changes from admin site.",
        long_description="\n".join((readme.read(), changes.read())),
        long_description_content_type="text/x-rst",
        author="Corey Bertram",
        author_email="corey@qr7.com",
        maintainer="Trey Hunner",
        url="https://github.com/jazzband/django-simple-history",
        project_urls={
            "Documentation": "https://django-simple-history.readthedocs.io/",
            "Changelog": "https://github.com/jazzband/django-simple-history/blob/master/CHANGES.rst",  # noqa: E501
            "Source": "https://github.com/jazzband/django-simple-history",
            "Tracker": "https://github.com/jazzband/django-simple-history/issues",
        },
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
            "Framework :: Django :: 3.2",
            "Framework :: Django :: 4.2",
            "Framework :: Django :: 5.0",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Programming Language :: Python :: 3.13",
            "License :: OSI Approved :: BSD License",
        ],
        python_requires=">=3.8",
        include_package_data=True,
    )
