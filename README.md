# zitadel-authorizer
Python Package for simpifying the use of Zitadel Token introspection with AWS API Gateway HTTP Integrations.

## Installation

```bash
# intall latest version
pip install --upgrade --force-reinstall git+https://github.com/rustyquill/zitadel-authorizer.git

# or install tagged release
pip install git+https://github.com/rustyquill/zitadel-authorizer.git@v0.1.0
```

## Development

```bash
# install all packages including the development requirements
pip install .[dev]
```

## Example Deployment

The [example](./example/) folder contains an example API Gateway Deployment with a custom lambda authorizer and endpoint using the package.

```bash
cd example

# bootstrap your aws account to allow for cdk deployments
# https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping-env.html
cdk boostrap

# synth and deploy the stack
cdk synth
cdk deploy
```

## Weblinks

- [Use Lambda Authorizers](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html)
- [Configure Lambda Authorizers](https://docs.aws.amazon.com/apigateway/latest/developerguide/configure-api-gateway-lambda-authorization.html)
- [Control access to HTTP APIs with AWS Lambda authorizers](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-lambda-authorizer.html)