from setuptools import setup, find_packages

with open("README.md") as readme_file:
    README = readme_file.read()

REQUIREMENTS = [
    "flask == 1.1.2",
    "flask_cors == 3.0.8",
    "webargs == 6.1.0",
    "pyyaml == 5.3.1",
]

setup(
    name="taransay-data",
    description="Taransay Data Service",
    long_description=README,
    author="Sean Leavey",
    author_email="electronics@attackllama.com",
    url="https://github.com/SeanDS/taransaydata/",
    use_scm_version={"write_to": "taransaydata/_version.py"},
    packages=find_packages(),
    python_requires=">=3.7",
    setup_requires=["setuptools_scm"],
    install_requires=REQUIREMENTS,
    extras_require={
        "dev": [
            "pytest",
            "pytest-flake8",
            "faker",
            "black",
            "pre-commit",
            "pylint",
            "flake8",
            "flake8-bugbear",
        ]
    },
    license="GPL-3.0-or-later",
    zip_safe=False,
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
