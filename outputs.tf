output "lambda_function_name" {
  value = aws_lambda_function.hello_lambda.function_name
}

output "s3_bucket_name" {
  value = aws_s3_bucket.my_bucket.bucket
}