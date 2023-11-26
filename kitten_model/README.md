# Get a quick model going

This document assumes you have aleready done the OIDC/IAM setup in the main README.

To use this to generate a model package to work with, please go to SageMaker and setup a Studio.

Then you can push this branch up and run the associated workflow.

When you push the branch `model-train` the workflow in this demo will create a model in the Amazon SageMaker Model Package Registry.

Any subsequent runs of this workflow will create a new version of the model. You can just push up a dummy change, or trigger the branch workflow in CCI.

Thanks to Timothy Cheung who's post I cribbed this from: [https://circleci.com/blog/machine-learning-ci-cd-with-aws-sagemaker/](https://circleci.com/blog/machine-learning-ci-cd-with-aws-sagemaker/)

This assumes you have setup the Environment Variable `SAGEMAKER_EXECUTION_ROLE_ARN` as descibed in the README.md in the root of this project.
