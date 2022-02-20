from setuptools import setup

from fielder_backend_utils import __version__

install_requires = [
    "djangorestframework>=3.11.0",
    "firebase-admin==5.2.0",
    "google-cloud-firestore==2.3.4",
    "google-cloud-tasks==2.0.0",
    "google-cloud-pubsub==2.2.0",
    "google-auth>=1.23.0,<2.0dev",
    "pyparsing<3",
    "pyjwt>=2.0.0",
    "requests>=2.25.1",
    "protobuf==3.19.0",
]

setup(
    name="fielder_backend_utils",
    version=__version__,
    description="Utilities for Fielder Backend",
    url="git@github.com:asomas/fielder-backend-utils",
    author="Sarmad Gulzar",
    author_email="sarmad@asomas.ai",
    license="MIT",
    packages=["fielder_backend_utils"],
    install_requires=install_requires,
    test_suite="tests",
    zip_safe=False,
)
