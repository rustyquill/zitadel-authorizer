#!/usr/bin/env node
import * as dotenv from "dotenv";
import path = require('path');
import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigatewayv2 from 'aws-cdk-lib/aws-apigatewayv2';
import * as apigatewayv2_integrations from 'aws-cdk-lib/aws-apigatewayv2-integrations';
import * as apigatewayv2_authorizers from 'aws-cdk-lib/aws-apigatewayv2-authorizers';

dotenv.config({ path: path.join(__dirname, '.env') });

const app = new cdk.App();
const stack = new cdk.Stack(app, 'ExampleHttpApiStack');

// build the authorizer lambda
const authorizerLambda = new lambda.Function(stack, 'AuthorizerLambda', {
    runtime: lambda.Runtime.PYTHON_3_13,
    handler: 'index.handler',
    environment: {
        POWERTOOLS_LOG_LEVEL: 'DEBUG',
        POWERTOOLS_SERVICE_NAME: 'zitadel-authorizer',
        // ISSUER_URL is your zitadel instances url
        ISSUER_URL: process.env.ISSUER_URL || "undefined",
        // INTROSPECTION_URL is used by the lambda to introspect the received token
        INTROSPECTION_ENDPOINT: process.env.INTROSPECTION_ENDPOINT || "undefined",
        // APPLICATION_KEY_ARN is used to retrieve the api private key from the parameter store
        APPLICATION_KEY_ARN: process.env.APPLICATION_KEY_ARN || "undefined",
    },
    architecture: lambda.Architecture.ARM_64,
    timeout: cdk.Duration.seconds(15),
    code: lambda.Code.fromAsset('..', {
        bundling: {
            image: lambda.Runtime.PYTHON_3_13.bundlingImage,
            bundlingFileAccess: cdk.BundlingFileAccess.VOLUME_COPY,
            user: 'root',
            platform: 'linux/arm64',
            environment: {
                PIP_CACHE_DIR: '/cache',
            },
            volumes: [
                {
                    hostPath: path.join(__dirname, 'lambda', 'authorizer', '.cache'),
                    containerPath: '/cache',
                }
            ],
            command: [
                'bash', '-c',
                `cd example/lambda/authorizer \\
                    && pip install --upgrade pip \\
                    && pip install -r requirements.txt -t /asset-output \\
                    && cp -au index.py /asset-output`
            ]
        }
    })
});
// allow the lambda to read the private key from the parameter store
authorizerLambda.addToRolePolicy(new cdk.aws_iam.PolicyStatement({
    actions: ['ssm:GetParameter'],
    resources: [process.env.APPLICATION_KEY_ARN || "undefined"],
}));

// build the service lambda
const serviceLambda = new lambda.Function(stack, 'ServiceLambda', {
    runtime: lambda.Runtime.PYTHON_3_13,
    handler: 'index.handler',
    environment: {
        POWERTOOLS_LOG_LEVEL: 'DEBUG',
        POWERTOOLS_SERVICE_NAME: 'service-lambda',
    },
    architecture: lambda.Architecture.ARM_64,
    timeout: cdk.Duration.seconds(15),
    code: lambda.Code.fromAsset('..', {
        bundling: {
            image: lambda.Runtime.PYTHON_3_13.bundlingImage,
            bundlingFileAccess: cdk.BundlingFileAccess.VOLUME_COPY,
            user: 'root',
            platform: 'linux/arm64',
            environment: {
                PIP_CACHE_DIR: '/cache',
            },
            volumes: [
                {
                    hostPath: path.join(__dirname, 'lambda', 'service', '.cache'),
                    containerPath: '/cache',
                }
            ],
            command: [
                'bash', '-c',
                `cd example/lambda/service \\
                    && pip install --upgrade pip \\
                    && pip install -r requirements.txt -t /asset-output \\
                    && cp -au index.py /asset-output`
            ]
        }
    })
});

const httpApi = new apigatewayv2.HttpApi(stack, 'HttpApi')
const httpBinIntegration = new apigatewayv2_integrations.HttpUrlIntegration('HttpBin', 'https://httpbin.org/anything');
const httpLambdaAuthorizer = new apigatewayv2_authorizers.HttpLambdaAuthorizer('ZitadelAuthorizer', authorizerLambda, {
    responseTypes: [apigatewayv2_authorizers.HttpLambdaResponseType.SIMPLE],
    identitySource: ['$request.header.Authorization'],
    resultsCacheTtl: cdk.Duration.seconds(300),
});
const httpLambdaIntegration = new apigatewayv2_integrations.HttpLambdaIntegration('ServiceLambda', serviceLambda, {
    payloadFormatVersion: apigatewayv2.PayloadFormatVersion.VERSION_2_0,
});

httpApi.addRoutes(
    {
        path: '/public/{proxy+}',
        methods: [apigatewayv2.HttpMethod.GET],
        integration: httpLambdaIntegration
    },
);

httpApi.addRoutes(
    {
        path: '/private/{proxy+}',
        methods: [apigatewayv2.HttpMethod.GET],
        integration: httpLambdaIntegration,
        authorizer: httpLambdaAuthorizer
    }
);
