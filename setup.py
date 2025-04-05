from setuptools import setup, find_packages

setup(
    name="zitadel-authorizer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Authlib>=1.5.2",
        "aws-lambda-powertools>=3.6.0",
        "cryptography",
        "pydantic>=2.10.6",
        "pydantic-settings>=2.8.1",
        "PyJWT>=2.10.1",
        "requests>=2.32.3",
    ],
    extras_require={
        "dev": ["pytest", "testcontainers", "moto[ssm]", "pkce"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)
