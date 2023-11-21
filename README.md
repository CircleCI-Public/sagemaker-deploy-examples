# Using AWS SageMaker Orb To Orchestrate Model Deployment Across Environments

## Pre-reqs

### Assumptions

* You have a model package in the SageMaker model registry. We provide an easy way to train one - please see the `kitten_model` folder READNE AFTER you finish reviewing this document.
* You know how to setup an IAM OIDC provider and setup a trust relationship for a role.

### OIDC

#### Identity Provider

The Amazon SageMaker Orb uses OIDC. You need to setup an IAM > Identity Provider in your AWS IAM for CircleCI OIDC Provider. You can read more on how to do that with our handy [guide](https://circleci.com/docs/openid-connect-tokens/).

#### Role

You will need an IAM > Role with the proper permissions:





You will then need to setup the Trust relationship between the Role and the CircleCI OIDC Provider. Here is an example Policy (Note you must replace the placeholders with your proper info):

```
{
	"Version": "2012-10-17",
	"Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::<AWS-ACCOUNT-ID>:oidc-provider/oidc.circleci.com/org/<CIRCLECI-ORG-ID>"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringLike": {
                    "oidc.circleci.com/org/<CIRCLECI-ORG-ID>:sub": "org/<CIRCLECI-ORG-ID>/project/<CIRCLECI-PROJECT-ID>/user/*"
                }
            }
        }
    ]
}
```

### Required Environment Variables

There are some required Environment Variables for the orb to function. Please configure these at either the Project level or using Org Contexts. [Guide on setting Environment Variables in CircleCI](https://circleci.com/docs/set-environment-variable/).

`SAGEMAKER_EXECUTION_ROLE_ARN` (required): This is the role you have configured with the necessary SageMaker permissions, and has the OIDC Trust relationship setup.

`CCI_RELEASE_INTEGRATION_TOKEN` (optional): The Orb also allows integration with [CircleCI Releases](https://app.circleci.com/releases). This will give you visibility into the Endpoint releases and what is currently active. To make a Release Integration Token please see our [Onboarding Guide](https://circleci.com/docs/release/set-up-a-release-environment/). [TODO Updated guide that mentions making the SageMaker Release Integration]

## Orb Parameters

`model_name` - The name of the model in SageMaker that we will be deploying.

`bucket` - This is the S3 bucket where resources will be stored.

`deploy_environment` - The name of the environment you are working with. This is an arbitrary string that works for how you like to organize your model deploys. Can be 'dev' or 'prod', for example.

`pipeline_id` - The pipeline.id is ued as a unique identifier for some of the configurations we create. Format: << pipeline.id >>

`region_name` - The aws region where the deployment is to happen. eg: `us-east-1`

`model_desc` - A description for the model to be deployed.

`project_id` - Found in the Project Settings in CircleCI. Used for specifying the project that triggered this deployment.

## Support

Stuck? Need help? Visit our [forums](https://discuss.circleci.com/) or come visit on [Discord](https://discord.com/invite/UWsWB44zYj).

