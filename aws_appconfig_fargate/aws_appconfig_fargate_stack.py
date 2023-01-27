from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_logs as logs,
    aws_iam as iam,
    aws_ecr as ecr,
    # Duration,
    Stack,
    CfnOutput,
    # aws_sqs as sqs,
)
from constructs import Construct


class AwsAppconfigFargateStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create VPC and Fargate Cluster
        # NOTE: Limit AZs to avoid reaching resource quotas
        # alternatively, you could look up existing VPCs here.
        vpc = ec2.Vpc(self, "MyVpc", max_azs=2)

        cluster = ecs.Cluster(self, "Ec2Cluster", vpc=vpc)

        # AWS repository with the agent
        appconfig_image = ecs.ContainerImage.from_registry(
            "public.ecr.aws/aws-appconfig/aws-appconfig-agent:latest"
        )

        # Your repository with an application image
        ecr_repository = ecr.Repository.from_repository_name(
            self, "flask-example", repository_name="your-repository"
        )
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "FargateService",
            cluster=cluster,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                container_port=5000,
                image=ecs.ContainerImage.from_ecr_repository(ecr_repository),
            ),
        )

        fargate_service.task_definition.add_container(
            "appConfig",
            image=appconfig_image,
            essential=True,
            port_mappings=[ecs.PortMapping(container_port=2772)],
            logging=ecs.LogDrivers.aws_logs(
                log_group=logs.LogGroup(
                    self,
                    "appconfig-example-lg",
                    log_group_name=f"/aws/fargate/app-config-example",
                    retention=logs.RetentionDays.ONE_WEEK,
                ),
                stream_prefix=f"appconfig-example",
            ),
        )

        fargate_service.task_definition.add_to_task_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=["*"],
                actions=[
                    "appconfig:StartConfigurationSession",
                    "appconfig:GetLatestConfiguration",
                ],
            )
        )

        fargate_service.service.connections.security_groups[0].add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(80),
            description="Allow http inbound from VPC",
        )

        CfnOutput(
            self,
            "LoadBalancerDNS",
            value=fargate_service.load_balancer.load_balancer_dns_name,
        )
