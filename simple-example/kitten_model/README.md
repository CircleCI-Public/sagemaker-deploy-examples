# Get a quick model going

When you push the branch `model-train` the workflow in this demo will create a model in the Amazon SageMaker registry.

Any subsequent runs of this workflow will create a new version of the model. You can just push up a dummy change, or trigger the branch workflow in CCI.

Thanks to Timothy Cheung who's post I cribbed this from: [https://circleci.com/blog/machine-learning-ci-cd-with-aws-sagemaker/](https://circleci.com/blog/machine-learning-ci-cd-with-aws-sagemaker/)

This assumes you have setup the Environment Variable `SAGEMAKER_EXECUTION_ROLE_ARN` as descibed in the simple-example README.md.
