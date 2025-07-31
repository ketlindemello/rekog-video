import boto3
import time
import sys

STACK_NAME = "rekog-python-file"  # Change if needed
REGION = "us-east-1"

def delete_stack(stack_name):
    cf = boto3.client("cloudformation", region_name=REGION)

    try:
        print(f"Requesting deletion of stack: {stack_name}")
        cf.delete_stack(StackName=stack_name)

        # Wait for the deletion to complete
        waiter = cf.get_waiter("stack_delete_complete")
        print("Waiting for stack deletion to complete...")
        waiter.wait(StackName=stack_name)
        print(f"✅ Stack '{stack_name}' deleted successfully.")
    except cf.exceptions.ClientError as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--yes":
        delete_stack(STACK_NAME)
    else:
        confirm = input(f"⚠️ Are you sure you want to delete the stack '{STACK_NAME}'? [y/N]: ").lower()
        if confirm == "y":
            delete_stack(STACK_NAME)
        else:
            print("❌ Deletion canceled.")
