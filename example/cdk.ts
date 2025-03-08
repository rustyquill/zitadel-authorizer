#!/usr/bin/env node
import path = require('path');
import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigatewayv2 from 'aws-cdk-lib/aws-apigatewayv2';
import * as apigatewayv2_integrations from 'aws-cdk-lib/aws-apigatewayv2-integrations';
import * as apigatewayv2_authorizers from 'aws-cdk-lib/aws-apigatewayv2-authorizers';

const app = new cdk.App();
const stack = new cdk.Stack(app, 'ExampleHttpApiStack');

// build the auhtorizer lambda
const authorizerLambda = new lambda.Function(stack, 'AuthorizerLambda', {
    runtime: lambda.Runtime.PYTHON_3_13,
    handler: 'index.handler',
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

const httpApi = new apigatewayv2.HttpApi(stack, 'HttpApi')
const httpBinIntegration = new apigatewayv2_integrations.HttpUrlIntegration('HttpBin', 'https://httpbin.org/anything');
const httpLambdaAuthorizer = new apigatewayv2_authorizers.HttpLambdaAuthorizer('ZitadelAuthorizer', authorizerLambda, {
    responseTypes: [apigatewayv2_authorizers.HttpLambdaResponseType.SIMPLE],
    identitySource: ['$request.header.Authorization'],
    resultsCacheTtl: cdk.Duration.seconds(300),
});

httpApi.addRoutes(
    {
        path: '/public',
        methods: [apigatewayv2.HttpMethod.GET],
        integration: httpBinIntegration
    },
);

httpApi.addRoutes(
    {
        path: '/private',
        methods: [apigatewayv2.HttpMethod.GET],
        integration: httpBinIntegration,
        authorizer: httpLambdaAuthorizer
    }
);
