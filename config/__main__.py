"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws
import iam
import json
import string
import random
from pulumi import ResourceOptions
from pulumi_command import local

region = aws.config.region

custom_stage_name = 'v1'

build = local.Command(''.join(random.choice(string.ascii_lowercase) for i in range(10)),
                      create="./scripts/build.sh"
                      )

##################
## Lambda Function
##################

# Create a Lambda function, using the zip created with the scripts/build.sh script.

lambda_func = aws.lambda_.Function("itc-api-imp",
                                   role=iam.lambda_role.arn,
                                   runtime="python3.9",
                                   handler="src/itc_api.handler",
                                   code=pulumi.FileArchive('./tmp/deployment-package.zip'),
                                   opts=ResourceOptions(depends_on=[build])
                                   )


####################################################################
##
## API Gateway REST API (API Gateway V1 / original)
##    /{proxy+} - passes all requests through to the lambda function
##
####################################################################
# Create a single Swagger spec route handler for a Lambda function.
def swagger_route_handler(arn, openapi_):
    openapi["paths"]["/{proxy+}"] = {
        "x-amazon-apigateway-any-method": {
            "x-amazon-apigateway-integration": {
                "uri": f'arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{arn}/invocations',
                "passthroughBehavior": "when_no_match",
                "httpMethod": "POST",
                "type": "aws_proxy",
            },
        },
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
rest_api = aws.apigateway.RestApi("api",
                                  body=lambda_func.arn.apply(
                                      lambda arn: json.dumps(swagger_route_handler(arn, openapi))))

# Create a deployment of the Rest API.
deployment = aws.apigateway.Deployment("api-deployment",
                                       rest_api=rest_api.id,
                                       # Note: Set to empty to avoid creating an implicit stage, we'll create it
                                       # explicitly below instead.
                                       stage_name="",
                                       )

# Create a stage, which is an addressable instance of the Rest API. Set it to point at the latest deployment.
stage = aws.apigateway.Stage("api-stage",
                             rest_api=rest_api.id,
                             deployment=deployment.id,
                             stage_name=custom_stage_name,
                             )

# Give permissions from API Gateway to invoke the Lambda
invoke_permission = aws.lambda_.Permission("api-lambda-permission",
                                           action="lambda:invokeFunction",
                                           function=lambda_func.name,
                                           principal="apigateway.amazonaws.com",
                                           source_arn=deployment.execution_arn.apply(lambda arn: arn + "*/*"),
                                           )

# Export the https endpoint of the running Rest API
pulumi.export("apigateway-rest-endpoint", deployment.invoke_url.apply(lambda url: url + custom_stage_name))
