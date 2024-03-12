# Kitten Model examples

## Get a quick model going

This document assumes you have already done the OIDC/IAM setup in the main README.

To use this to generate a model package to work with, please go to SageMaker and setup a Studio.

Then you can push this branch up and run the associated workflow.

When you push the branch `model-train` the workflow in this demo will create a model in the Amazon SageMaker Model Package Registry.

Any subsequent runs of this workflow will create a new version of the model. You can just push up a dummy change, or trigger the branch workflow in CCI.

Thanks to Timothy Cheung who's post I cribbed this from: [https://circleci.com/blog/machine-learning-ci-cd-with-aws-sagemaker/](https://circleci.com/blog/machine-learning-ci-cd-with-aws-sagemaker/)

This assumes you have setup the Environment Variable `SAGEMAKER_EXECUTION_ROLE_ARN` as descibed in the README.md in the root of this project.

## Invoking and evaluating the model

The creation of your model must be completed before this step is possible. The `invoke_and_eval.py` script gives you the framework you can use to perform the necessary tasks. It shows you, in python, how to:

1. auth using the OIDC steps previously prepped
1. prepare your data for invocation
1. invoke the created endpoint (dev)
1. receive your results

In `.config/circle.yml`, you can see how this script could be run as a gate to promoting your model to a production environment.
