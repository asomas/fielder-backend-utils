from setuptools import setup

install_requires = [
    'firebase-admin>=4.4.0',
    'google-auth>=1.23.0',
    'djangorestframework>=3.11.0',
]

setup(
    name="fielder_backend_utils",
    version="0.0.1",
    description="Utilities for Fielder Backend",
    url="git@github.com:asomas/fielder-backend-utils",
    author="Sarmad Gulzar",
    author_email="sarmad@asomas.ai",
    license="MIT",
    packages=["fielder_backend_utils"],
    install_requires=install_requires, 
    test_suite="tests",   
    zip_safe=False
)