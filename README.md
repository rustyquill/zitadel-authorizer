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

### Zitadel

Run the docker compose file, once the zitadel server has started you can access it via http://localhost:8080/ui/console.

Username: admin@zitadel.localhost
Password: admin

## Example Deployment

The [example](./example/) folder contains an example API Gateway Deployment with a custom lambda authorizer and endpoint using the package.

### Requirements

- You need an AWS account to deploy the API gateway and Lambdas
- You need [aws cdk](https://aws.amazon.com/cdk/) installed
- You need Postman installed to impport the [postman collection](./example/zitadel_authorizer%20-%20Example.postman_collection.json)
- Your Zitadel instance needs to be publicly accessible.
- Create a new project in your zitadel instance
- Create an API application in the project. This app will be used by the API Gateway authorizer lambda to introspect the given user token.
  - Generate a JSON key for the API application
  - Download the key file and convert it to a base64 encoded string
  - Convert the whole file to a base64 encoded string and seve it in your AWS account in the Parameter Store as a Secure String
- Copy the [./examples/.env.example](./example/.env.example) file to [./examples/.env](./examples/.env) and replace its values
- Create a new SPA or Web application with PKCE and `Bearer Token` as Auth Token Type
- Import the postman collection [zitadel_authorizer - Example.postman_collection.json](./example/zitadel_authorizer%20-%20Example.postman_collection.json) into your postman.
  - Replace the variable `zitadel_url` with the url of your zitadel instance
  - Replace the variable `client_id` with the client id of your SPA or web application.
  - You can now lease new access tokens using postman and use the token to call the API once it's deployed!
- Deploy the API Gateway and lambdas using aws cdk

```bash
cd example

# bootstrap your aws account to allow for cdk deployments
# https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping-env.html
cdk boostrap

# synth and deploy the stack
cdk deploy
```

- Once deployed get the API gateway invoke url - open the AWS console, navigate to API Gateway -> Stages -> Default and copy the invoke url.
- Open the postman collection and replace the variables `api_base_url` with the api gateways invoke url

## Weblinks

- [Use Lambda Authorizers](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html)
- [Configure Lambda Authorizers](https://docs.aws.amazon.com/apigateway/latest/developerguide/configure-api-gateway-lambda-authorization.html)
- [Control access to HTTP APIs with AWS Lambda authorizers](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-lambda-authorizer.html)
- [api gateway authorizer blueprint](https://github.com/awslabs/aws-apigateway-lambda-authorizer-blueprints/blob/master/blueprints/python/api-gateway-authorizer-python.py)