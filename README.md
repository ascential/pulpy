# Pulpy
Infrastructure as Code (IaC) based on Pulumi, Python and YAML template files.

## Content
This repository contains a series of Python packages and modules for various cloud providers like AWS, GCP, Alibaba Cloud, Azure etc. and their associated services.

## How to use Pulpy
Pulpy should be used only as a git sub-module within your main IaC project.

## Requirements
Before creating a new project make sure you have the below tools installed on your local or remote machine.
- Pulumi ([details](https://www.pulumi.com/docs/get-started/install/))
- Git Client
- CLI access to your desired Cloud Provider(s), preferably using service account(s)

## Releases
- v1.0.0 - The very first Pulpy release containing modules only for AWS package:
    * aws/vpc
    * aws/subnet
    * aws/internetgateway
    * aws/natgateway
    * aws/routetable
    * aws/elasticip
    * aws/securitygroup
    * aws/iam
    * aws/keypair
    * aws/ec2
    * aws/elasticache
    * aws/documentdb
    * aws/rds
    * aws/eks
    * aws/s3
    * aws/loadbalancer
    * aws/mandatory
