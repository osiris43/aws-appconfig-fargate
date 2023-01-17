import aws_cdk as core
import aws_cdk.assertions as assertions

from aws_appconfig_fargate.aws_appconfig_fargate_stack import AwsAppconfigFargateStack

# example tests. To run these tests, uncomment this file along with the example
# resource in aws_appconfig_fargate/aws_appconfig_fargate_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AwsAppconfigFargateStack(app, "aws-appconfig-fargate")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
