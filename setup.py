from setuptools import setup

install_requires = [
    "djangorestframework>=3.11.0",
    "firebase-admin==4.4.0",
    "google-cloud-firestore==2.0.2",
    "google-auth>=1.23.0,<2.0dev",
    "pyparsing<3",
    "pyjwt>=2.0.0",
    "requests>=2.25.1",
]

setup(
    name="fielder_backend_utils",
    version="1.0.16",
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
