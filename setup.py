from setuptools import setup, find_packages

setup(
    name="zitadel-authorizer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic==2.10.6",
        "PyJWT==2.10.1",
        "cryptography",
        "aws-lambda-powertools==3.6.0",
    ],
    extras_require={
        "dev": [
            "pytest",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)
