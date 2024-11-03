# Configure AWS Provider
provider "aws" {
  region = "us-west-2"
}

# Import existing S3 bucket
import {
  to = aws_s3_bucket.lambda_bucket
  id = "knowyourleague-backfill-lambda-bucket"
}

# Create/Import S3 bucket for Lambda code
resource "aws_s3_bucket" "lambda_bucket" {
  bucket = "knowyourleague-backfill-lambda-bucket"
  tags = {
    Name        = "KnowYourLeague Lambda Code Bucket"
    Environment = "production"
  }
}

# Import existing IAM role
import {
  to = aws_iam_role.lambda_role
  id = "knowyourleague_backfill_lambda_role"
}

# Create/Import IAM role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "knowyourleague_backfill_lambda_role"
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

# Enable versioning on the S3 bucket
resource "aws_s3_bucket_versioning" "lambda_bucket_versioning" {
  bucket = aws_s3_bucket.lambda_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Attach basic Lambda execution policy
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_role.name
}

# Upload the Lambda code to S3
resource "aws_s3_object" "lambda_code" {
  bucket = aws_s3_bucket.lambda_bucket.id
  key    = "lambda.zip"
  source = "${path.module}/../dist/function.zip"
  etag   = filemd5("${path.module}/../dist/function.zip")
}

# Create Lambda function
resource "aws_lambda_function" "backfill_lambda" {
  function_name = "knowyourleague_backfill_lambda"
  description   = "Lambda function for KnowYourLeague data backfilling"
  
  s3_bucket = aws_s3_bucket.lambda_bucket.id
  s3_key    = aws_s3_object.lambda_code.key
  
  runtime = "nodejs18.x"
  handler = "handler.lambda_handler"
  
  role = aws_iam_role.lambda_role.arn
  
  environment {
    variables = {
      ENVIRONMENT = "production"
    }
  }

  tags = {
    Name        = "KnowYourLeague Backfill Lambda"
    Environment = "production"
  }
}

# Add CloudWatch Log Group with retention
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.backfill_lambda.function_name}"
  retention_in_days = 30
}

# Outputs
output "lambda_function_arn" {
  description = "The ARN of the Lambda function"
  value       = aws_lambda_function.backfill_lambda.arn
}

output "s3_bucket_name" {
  description = "The name of the S3 bucket"
  value       = aws_s3_bucket.lambda_bucket.id
}