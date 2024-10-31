# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-1"
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket containing Lambda code"
  type        = string
}

variable "s3_key_prefix" {
  description = "Prefix for Lambda code in S3 bucket"
  type        = string
  default     = "lambda/"
}

# Provider configuration
provider "aws" {
  region = var.aws_region
}

# S3 bucket notification configuration
resource "aws_s3_bucket_notification" "lambda_trigger" {
  bucket = var.s3_bucket_name

  lambda_function {
    lambda_function_arn = aws_lambda_function.updater.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = var.s3_key_prefix
  }
}

# Main Lambda function
resource "aws_lambda_function" "main" {
  filename         = "initial-dummy.zip"  # Initial placeholder
  function_name    = "s3-sourced-lambda"
  role            = aws_iam_role.lambda_role.arn
  handler         = "index.handler"
  runtime         = "nodejs18.x"  # Adjust based on your needs
  timeout         = 30
  publish         = true

  lifecycle {
    ignore_changes = [filename, source_code_hash]  # Ignore local file changes as code will come from S3
  }
}

# Updater Lambda function
resource "aws_lambda_function" "updater" {
  filename      = data.archive_file.updater_zip.output_path
  function_name = "lambda-code-updater"
  role         = aws_iam_role.updater_role.arn
  handler      = "index.handler"
  runtime      = "nodejs18.x"
  timeout      = 30

  environment {
    variables = {
      TARGET_FUNCTION_NAME = aws_lambda_function.main.function_name
    }
  }
}

# Zip file for updater Lambda
data "archive_file" "updater_zip" {
  type        = "zip"
  output_path = "${path.module}/updater.zip"

  source {
    content  = <<EOF
const AWS = require('aws-sdk');
const lambda = new AWS.Lambda();

exports.handler = async (event) => {
  const bucket = event.Records[0].s3.bucket.name;
  const key = event.Records[0].s3.object.key;
  
  const params = {
    FunctionName: process.env.TARGET_FUNCTION_NAME,
    S3Bucket: bucket,
    S3Key: key,
    Publish: true
  };
  
  try {
    await lambda.updateFunctionCode(params).promise();
    console.log(`Successfully updated function code from ${bucket}/${key}`);
  } catch (error) {
    console.error('Error updating function:', error);
    throw error;
  }
};
EOF
    filename = "index.js"
  }
}

# Main Lambda IAM role
resource "aws_iam_role" "lambda_role" {
  name = "s3-sourced-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Updater Lambda IAM role
resource "aws_iam_role" "updater_role" {
  name = "lambda-updater-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Lambda basic execution policy attachment
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "updater_basic" {
  role       = aws_iam_role.updater_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# S3 access policy for main Lambda
resource "aws_iam_role_policy" "lambda_s3_access" {
  name = "s3-access"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.s3_bucket_name}",
          "arn:aws:s3:::${var.s3_bucket_name}/*"
        ]
      }
    ]
  })
}

# Lambda update policy for updater function
resource "aws_iam_role_policy" "updater_lambda_access" {
  name = "lambda-update"
  role = aws_iam_role.updater_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:UpdateFunctionCode",
          "lambda:PublishVersion"
        ]
        Resource = aws_lambda_function.main.arn
      }
    ]
  })
}

# Permission for S3 to invoke updater Lambda
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.updater.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = "arn:aws:s3:::${var.s3_bucket_name}"
}