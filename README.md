# aws-cost-optimizer
🧹 AWS Lambda – EBS Snapshot Cleanup for Cloud Cost Optimization

This project is a serverless solution using AWS Lambda to identify and automatically delete stale EBS snapshots (those no longer attached to active volumes or EC2 instances), helping you reduce unnecessary cloud storage costs.

💡 This approach can be extended to other AWS resources like unused Elastic IPs, old Lambda versions, orphaned EBS volumes, etc.

✅ Features

🔍 Scans all snapshots owned by your account

🧠 Checks whether the associated volume/instance is active

🗑️ Deletes stale or unused snapshots

📬 Sends real-time notifications via SNS

⏰ Triggered on schedule using CloudWatch Events

🛠️ Technologies Used

AWS Lambda (Python)

Amazon EC2

Amazon SNS

Amazon CloudWatch

IAM Roles & Policies



🚀 Setup Guide

1. Deploy Lambda Function

Create a Lambda function in the AWS console using lambda_function.py

Set the runtime to Python 3.9+



2. Set Environment Variables

Variable

Description

SNS_TOPIC_ARN

ARN of the SNS topic for notifications

DRY_RUN

Set to true for testing, false to actually delete

PROTECT_TAG_KEY

(Optional) Snapshots with this tag key will be skipped




3. IAM Role Permissions

Attach a role with the following permissions:
{
  "Effect": "Allow",
  "Action": [
    "ec2:DescribeSnapshots",
    "ec2:DeleteSnapshot",
    "ec2:DescribeVolumes",
    "ec2:DescribeInstances",
    "sns:Publish"
  ],
  "Resource": "*"
}

✅ Least privilege is recommended for production.



4. Configure SNS
Create an SNS topic

Subscribe your email or Slack webhook to get notifications

Pass the SNS Topic ARN as an environment variable



5. Setup CloudWatch Schedule
Go to CloudWatch → Rules → Create Rule

Choose EventBridge (Scheduler) → cron schedule (e.g. rate(1 day))

Target: Your Lambda function



🧪 Testing
Set DRY_RUN=true to log deletions without actually deleting

Check logs in CloudWatch Logs

Confirm notifications from SNS


✅ Key Notes:
DRY_RUN: Set environment variable DRY_RUN = false to enable actual deletion.

SNS_TOPIC_ARN: Provide this as an environment variable to receive email/Slack alerts.

PROTECT_TAG_KEY: You can tag snapshots with this key (e.g. KeepSnapshot) to skip deletion.



💻 Author
Saad — DevOps & Cloud Enthusiast

Linkedin https://www.linkedin.com/in/saad-patel-469016314/ 
GitHub https://github.com/Saadp001
