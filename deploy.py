import os
import shutil
import subprocess
import tempfile

REGION = "us-east-1"
BUCKET = "cloud-formation-serverless-deployments"
KEY = "lambdas/imagerecognitionlambda/imagegenrecog-1.0.zip"
STACK_NAME = "rekog-python-file"
ZIP_NAME = "imagegenrecog-1.0.zip"
LAMBDA_SRC = "src"  # Where your lambda_handler.py is
REQUIREMENTS = "requirements.txt"

def run_cmd(cmd, cwd=None):
    print(f"\nRunning: {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=cwd)


def package_lambda():
    print("📦 Packaging Lambda function with dependencies...")

    with tempfile.TemporaryDirectory() as build_dir:
        # Install requirements into build_dir
        if os.path.exists(REQUIREMENTS):
            run_cmd([
                "pip", "install",
                "-r", REQUIREMENTS,
                "-t", build_dir
            ])
        else:
            print("⚠️ No requirements.txt found. Skipping dependency install.")

        # Copy source files into build_dir
        for item in os.listdir(LAMBDA_SRC):
            src_path = os.path.join(LAMBDA_SRC, item)
            dest_path = os.path.join(build_dir, item)
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
            else:
                shutil.copy2(src_path, dest_path)

        # Zip contents of build_dir into ZIP_NAME
        shutil.make_archive(ZIP_NAME.replace(".zip", ""), 'zip', root_dir=build_dir)

    print(f"✅ Lambda package created: {ZIP_NAME}")


def upload_to_s3():
    print(f"⬆️ Uploading {ZIP_NAME} to S3 bucket {BUCKET}...")
    run_cmd([
        "aws", "s3", "cp", ZIP_NAME,
        f"s3://{BUCKET}/{KEY}",
        "--region", REGION
    ])
    print(f"✅ Uploaded {ZIP_NAME} to s3://{BUCKET}/{KEY}")


def deploy_cloudformation():
    print(f"🚀 Deploying CloudFormation stack {STACK_NAME}...")
    run_cmd([
        "aws", "cloudformation", "deploy",
        "--template-file", "config.yaml",
        "--stack-name", STACK_NAME,
        "--capabilities", "CAPABILITY_NAMED_IAM",
        "--region", REGION,
        "--no-fail-on-empty-changeset"
    ])
    print(f"✅ CloudFormation stack created or updated: {STACK_NAME}")

    # Optional: show stack outputs
    run_cmd([
        "aws", "cloudformation", "describe-stacks",
        "--stack-name", STACK_NAME,
        "--region", REGION,
        "--query", "Stacks[0].Outputs"
    ])


def main():
    package_lambda()
    upload_to_s3()
    deploy_cloudformation()


if __name__ == "__main__":
    main()
