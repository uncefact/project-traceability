"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws
import iam
import json
import string
import random
import hashlib
from pulumi import ResourceOptions
from pulumi import Output

region = aws.config.region
config = pulumi.Config();
data = config.require_object("imp")
login_url = data.get('login-url')
custom_stage_name = data.get('custom-stage-name')

#build = local.Command(''.join(random.choice(string.ascii_lowercase) for i in range(10)),
#                      create="./scripts/build.sh"
#                      )

##################
## Lambda Function
##################

# Create a Lambda function, using the zip created with the scripts/build.sh script.

lambda_func = aws.lambda_.Function("itc-api-imp",
                                   role=iam.lambda_role.arn,
                                   runtime="python3.9",
                                   handler="src/itc_api.handler",
                                   environment={
                                       "variables": {
                                           'LOGIN_URL': login_url
                                       },
                                   },
                                   code=pulumi.FileArchive('./tmp/deployment-package.zip')#,
                                   #opts=ResourceOptions(depends_on=[build])
                                   )


####################################################################
##
## API Gateway REST API (API Gateway V1 / original)
##    /{proxy+} - passes all requests through to the lambda function
##
####################################################################
# Create a single Swagger spec route handler for a Lambda function.

def swagger_route_handler(arns, openapi_):
    openapi_["components"]["securitySchemes"]["UserPool"] = {
        "type": "apiKey",
        "name": "Authorization",
        "in": "header",
        "x-amazon-apigateway-authtype": "cognito_user_pools",
        "x-amazon-apigateway-authorizer": {
            "type": "cognito_user_pools",
            "providerARNs": [
                arns[0]
            ]
        }
    }
    for path in openapi_["paths"].keys():
        for method in openapi_["paths"][path].keys():
            openapi_["paths"][path][method]["x-amazon-apigateway-integration"] = {
                "uri": f'arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{arns[1]}/invocations',
                "passthroughBehavior": "when_no_match",
                "httpMethod": "POST",
                "type": "aws_proxy",
            }
            openapi_["paths"][path][method]["security"] = [
                {
                   "UserPool": []
                }
            ]
    openapi_["paths"]["/redoc"] = {
        "get": {
            "x-amazon-apigateway-integration": {
                "uri": f'arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{arns[1]}/invocations',
                "passthroughBehavior": "when_no_match",
                "httpMethod": "POST",
                "type": "aws_proxy"
            }
        }
    }

    openapi_["paths"]["/docs"] = {
        "get": {
            "x-amazon-apigateway-integration": {
                "uri": f'arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{arns[1]}/invocations',
                "passthroughBehavior": "when_no_match",
                "httpMethod": "POST",
                "type": "aws_proxy"
            }
        }
    }

    openapi_["paths"]["/"] = {
        "get": {
            "x-amazon-apigateway-integration": {
                "uri": f'arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{arns[1]}/invocations',
                "passthroughBehavior": "when_no_match",
                "httpMethod": "POST",
                "type": "aws_proxy"
            }
        }
    }

    openapi_["paths"]["/openapi.json"] = {
        "get": {
            "x-amazon-apigateway-integration": {
                "uri": f'arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{arns[1]}/invocations',
                "passthroughBehavior": "when_no_match",
                "httpMethod": "POST",
                "type": "aws_proxy"
            }
        }
    }
    return openapi_

# TODO: figure out how to create the api gateway with one step
# at the moment the resource creation fails if the code below isn't being executed first
# openapi = {
#     "swagger": "2.0",
#     "info": {"title": "api", "version": "1.0"},
#     "paths": {},
# }
#
# rest_api = aws.apigateway.RestApi("api",
#                                   body=lambda_func.arn.apply(lambda arn: json.dumps(swagger_route_handler(arn, openapi))))


with open("../api/openapi.json", encoding="utf-8") as f:
    read_data = f.read()
f.closed

openapi = json.loads(read_data);


pool = aws.cognito.UserPool("user-pool",
                            username_attributes = ['email'],
                            username_configuration = aws.cognito.UserPoolUsernameConfigurationArgs(
                                case_sensitive= False)
                            )

rest_api = aws.apigateway.RestApi("api",
                                  body=Output.all(pool.arn, lambda_func.arn)
                                  .apply(lambda arns: json.dumps(swagger_route_handler(arns, openapi))),
                                  opts=ResourceOptions(depends_on=[pool]))

# Create a deployment of the Rest API.
deployment = aws.apigateway.Deployment("api-deployment",
                                        rest_api=rest_api.id,
                                        # Note: Set to empty to avoid creating an implicit stage, we'll create it
                                        # explicitly below instead.
                                        stage_name=custom_stage_name,
                                        triggers={
                                         "redeployment": rest_api.body.apply(lambda body: json.dumps(body)).apply(
                                             lambda to_json: hashlib.sha1(to_json.encode()).hexdigest()),
                                        }
                                       )

# Create a stage, which is an addressable instance of the Rest API. Set it to point at the latest deployment.
stage = aws.apigateway.Stage("api-stage",
                             rest_api=rest_api.id,
                             deployment=deployment.id,
                             stage_name=custom_stage_name
                             )

# Give permissions from API Gateway to invoke the Lambda
invoke_permission = aws.lambda_.Permission("api-lambda-permission",
                                           action="lambda:invokeFunction",
                                           function=lambda_func.name,
                                           principal="apigateway.amazonaws.com",
                                           source_arn=deployment.execution_arn.apply(lambda arn: arn + "*/*"),
                                           )
# Creates an AWS resource (S3 Bucket)
bucket = aws.s3.Bucket(
    'github-idp-bucket'
)


userpool_client = aws.cognito.UserPoolClient("userpoolClient",
    user_pool_id=pool.id,
    callback_urls=[deployment.invoke_url.apply(lambda url: url+'?')],
    allowed_oauth_flows_user_pool_client=True,
    allowed_oauth_flows=[
        "implicit",
    ],
    allowed_oauth_scopes=[
        "openid",
    ],
    supported_identity_providers=["COGNITO","GitHubShim"])


# Export the https endpoint of the running Rest API
pulumi.export("apigateway-rest-endpoint", deployment.invoke_url.apply(lambda url: url))
pulumi.export('bucket_name', bucket.bucket)
