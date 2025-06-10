
# Terraform Lambda + S3 Example

This example repo shows how to deploy:

✅ A simple Lambda function that prints "Hello World"  
✅ An S3 bucket

### Usage

1. Add AWS credentials as GitHub Secrets:
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY

2. Push this repo to GitHub

3. On push to `main`, GitHub Actions will:
- Run Terraform Init, Plan, Apply
- Deploy the Lambda + S3

4. You can test the Lambda manually in AWS Console → Lambda → HelloWorldLambda

Enjoy! 🚀
