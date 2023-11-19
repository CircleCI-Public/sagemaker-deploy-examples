import boto3
import os
import sagemaker

bucket = os.environ["BUCKET_NAME"]
model_name = os.environ["MODEL_NAME"]
region_name = os.environ["REGION_NAME"]
role_arn = os.environ["SAGEMAKER_EXECUTION_ROLE_ARN"]
web_identity_token = os.environ["CIRCLE_OIDC_TOKEN"]


# Set up the session and client we will need for this step
role = boto3.client("sts").assume_role_with_web_identity(
    RoleArn=role_arn, RoleSessionName="assume-role", WebIdentityToken=web_identity_token
)
credentials = role["Credentials"]
aws_access_key_id = credentials["AccessKeyId"]
aws_secret_access_key = credentials["SecretAccessKey"]
aws_session_token = credentials["SessionToken"]
boto_session = boto3.Session(
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    aws_session_token=aws_session_token,
)
sagemaker_client = boto_session.client(service_name="sagemaker")
sagemaker_runtime_client = boto_session.client(service_name="sagemaker-runtime")
sagemaker_session = sagemaker.Session(
    boto_session=boto_session,
    sagemaker_client=sagemaker_client,
    sagemaker_runtime_client=sagemaker_runtime_client,
    default_bucket=bucket,
)
s3_client = boto_session.client(service_name="s3")


# Data retrieval and processing taken from
# https://github.com/aws/amazon-sagemaker-examples/blob/main/introduction_to_amazon_algorithms/xgboost_abalone/xgboost_abalone.ipynb
# You would likely replace this part for your own use case, such as querying from Snowflake or Redshift

# S3 bucket where the training data is located
data_bucket = f"sagemaker-sample-files"
data_prefix = "datasets/tabular/uci_abalone"

for data_category in ["train", "validation"]:
    data_key = "{0}/{1}/abalone.{1}".format(data_prefix, data_category)
    output_key = "{0}/{1}/{1}.libsvm".format(model_name, data_category)
    data_filename = "abalone.{}".format(data_category)
    s3_client.download_file(data_bucket, data_key, data_filename)
    s3_client.upload_file(data_filename, bucket, output_key)
