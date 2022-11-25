from setuptools import find_packages, setup

from fielder_backend_utils import __version__

install_requires = [
    "black~=22.10.0",
    "wheel~=0.38.0",
    "djangorestframework~=3.12.4",
    "Django~=4.1.2",
    "django-cors-headers~=3.13.0",
    "firebase-admin~=6.0.1",
    "google-cloud-firestore~=2.7.2",
    "google-cloud-secret-manager~=2.12.6",
    "google-cloud-tasks~=2.10.4",
    "google-cloud-pubsub~=2.13.10",
    "google-auth~=2.13.0",
    "gunicorn~=20.1.0",
    "lxml~=4.9.0",
    "pyjwt~=2.6.0",
    "pyparsing~=3.0.9",
    "python-i18n~=0.3.9",
    "PyYAML==6.0",
    "requests~=2.28.1",
    "sentry-sdk~=1.9.10",
]

setup(
    name="fielder_backend_utils",
    version=__version__,
    description="Utilities for Fielder Backend",
    url="git@github.com:asomas/fielder-backend-utils",
    author="Sarmad Gulzar",
    author_email="sarmad@asomas.ai",
    license="MIT",
    install_requires=install_requires,
    test_suite="tests",
    zip_safe=False,
    packages=find_packages(),
)
