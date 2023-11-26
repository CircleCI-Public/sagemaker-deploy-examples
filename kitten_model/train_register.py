import sagemaker
from sagemaker.estimator import Estimator
from sagemaker.inputs import TrainingInput
import boto3
import os

bucket = os.environ["BUCKET_NAME"]
model_name = os.environ["MODEL_NAME"]
model_description = os.environ["MODEL_DESC"]
region_name = os.environ["REGION_NAME"]
role_arn = os.environ["SAGEMAKER_EXECUTION_ROLE_ARN"]
web_identity_token = os.environ["CIRCLE_OIDC_TOKEN"]


# Set up the sessions and clients we will need for this step
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


# Set up dataset locations
train_set_location = f"s3://{bucket}/{model_name}/train/"
validation_set_location = f"s3://{bucket}/{model_name}/validation/"
model_location = f"s3://{bucket}/{model_name}/model/"

train_set_pointer = TrainingInput(s3_data=train_set_location, content_type="libsvm")
validation_set_pointer = TrainingInput(
    s3_data=validation_set_location, content_type="libsvm"
)

# Retrieve xgboost image
image_uri = sagemaker.image_uris.retrieve(
    framework="xgboost", region=region_name, version="1.5-1"
)

# Configure training estimator
xgb_estimator = Estimator(
    base_job_name=model_name,
    image_uri=image_uri,
    instance_type="ml.m5.large",
    instance_count=1,
    output_path=model_location,
    sagemaker_session=sagemaker_session,
    role=role_arn,
    hyperparameters={
        "objective": "reg:linear",
        "max_depth": 1,
        "eta": 0.2,
        "gamma": 4,
        "min_child_weight": 6,
        "subsample": 0.7,
        "verbosity": 2,
        "num_round": 1,
    },
)

xgb_estimator.fit({"train": train_set_pointer, "validation": validation_set_pointer})

training_job_name = xgb_estimator.latest_training_job.job_name
print("training_job_name:", training_job_name)


# In this section, we push the newly trained model to the model registry,
# so that we may subsequently refer to it during deployment.
# Check if model_name already exists as a model group in the model registry
matching_mpg = sagemaker_client.list_model_package_groups(NameContains=model_name)[
    "ModelPackageGroupSummaryList"
]

if matching_mpg:
    print(f"Using existing Model Package Group: {model_name}")
else:
    mpg_input_dict = {
        "ModelPackageGroupName": model_name,
        "ModelPackageGroupDescription": model_description,
    }
    mpg_response = sagemaker_client.create_model_package_group(**mpg_input_dict)
    mpg_arn = mpg_response["ModelPackageGroupArn"]
    print(f"Created new Model Package Group: {model_name}, ARN: {mpg_arn}")


# Retrieve model artifacts from training job
model_artifacts = xgb_estimator.model_data

# Create pre-approved cross-account model package
create_model_package_input_dict = {
    "ModelPackageGroupName": model_name,
    "ModelPackageDescription": "",
    "ModelApprovalStatus": "Approved",
    "InferenceSpecification": {
        "Containers": [{"Image": image_uri, "ModelDataUrl": model_artifacts}],
        "SupportedContentTypes": ["text/csv"],
        "SupportedResponseMIMETypes": ["text/csv"],
    },
}

create_model_package_response = sagemaker_client.create_model_package(
    **create_model_package_input_dict
)
print(f"Model Package version ARN: {create_model_package_response['ModelPackageArn']}")
