import pandas as pd
import boto3
import sagemaker
import io
from io import StringIO
import os
import math
from pprint import pprint

###############################################################################
# This section sets up necessary variables from the environment
###############################################################################
bucket = os.environ["BUCKET_NAME"]
model_name = os.environ["MODEL_NAME"]
region_name = os.environ["REGION_NAME"]
role_arn = os.environ["SAGEMAKER_EXECUTION_ROLE_ARN"]
web_identity_token = os.environ["CIRCLE_OIDC_TOKEN"]

###############################################################################
# This section authenticates and sets up the sagemaker client
###############################################################################
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

###############################################################################
# This section is for setting up your inputs that will be send to the model
#
# While this is a sample, inputs (and formats) pertinent to your model will
# be required here to get results that you can reasonably validate later
###############################################################################
read_bucket = "sagemaker-sample-files"
read_prefix = "datasets/tabular/uci_abalone/test_csv"

# # S3 location of test data
test_data_uri = f"s3://{read_bucket}/{read_prefix}/abalone_dataset1_test.csv" 
test_df = pd.read_csv(test_data_uri)

# This is the inference request serialization step
# CSV serialization
csv_file = io.StringIO()
test_df.to_csv(csv_file, sep=",", header=False, index=False)
payload = csv_file.getvalue()

###############################################################################
# This section is where the inputs are sent to your trained model
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sagemaker-runtime/client/invoke_endpoint.html
#
# The endpoint name will be the dev variant, before approving for prod deploy
###############################################################################
endpoint_name=model_name + "-dev"
response = sagemaker_runtime_client.invoke_endpoint(
            EndpointName=endpoint_name,
            Body=payload,
            ContentType="text/csv",
            Accept="text/csv"
            )

###############################################################################
# This section is where you can extract and interpret the results
#
# Again, this will be specific to your model, and you can use this to
# print results, and even throw errors, to help decide if the current model
# is ready for production deployment
###############################################################################
result = response["Body"].read()
# Decoding bytes to a string
result = result.decode("utf-8")
# Converting to list of predictions
result = result.strip("\n").split("\n")
result = [math.ceil(float(i)) for i in result]
prediction_df = pd.DataFrame()
prediction_df["Prediction"] = result[:5]
print(prediction_df)
