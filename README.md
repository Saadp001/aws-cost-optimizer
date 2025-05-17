<h1 align="center">🧹 AWS Lambda – EBS Snapshot Cleanup</h1>

<p align="center">
  <img src="https://img.shields.io/badge/AWS-Lambda-orange?logo=amazon-aws&style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Cost‑Optimization-%F0%9F%92%B2-success?style=for-the-badge"/>
  <img src="https://img.shields.io/github/license/Saadp001/aws-cost-optimizer?style=for-the-badge"/>
</p>

**Serverless solution** that **scans and deletes stale EBS snapshots** (no longer attached to any active EC2 volumes), automatically reducing storage costs.  
> 💡 Easily extendable to other unused resources—Elastic IPs, orphaned EBS volumes, old Lambda versions, etc.

---

## ✨ Features
- 🔍 Scans **all snapshots** in the account  
- 🧠 Verifies associated volume or instance status  
- 🗑️ Deletes snapshots that are no longer needed *(optional **DRY‑RUN** mode)*  
- 📬 Sends **real‑time SNS notifications** (email / Slack)  
- ⏰ Runs on a **CloudWatch Events (EventBridge)** schedule

---

## 🛠️ Tech Stack
| Service | Purpose |
|---------|---------|
| **AWS Lambda (Python 3.9+)** | Core cleanup logic |
| **Amazon EC2 / EBS** | Resources being optimized |
| **Amazon SNS** | Notifications |
| **Amazon CloudWatch** | Scheduling & logging |
| **IAM** | Least‑privilege permissions |

---

## 🚀 Quick Start

### 1. Deploy Lambda
1. Create a new Lambda function.  
2. Copy `lambda/lambda_function.py` (this repo) into the code editor.  
3. Runtime ➜ **Python 3.9** (or newer).

### 2. Set Environment Variables

| Key               | Example Value                                          | Notes                                   |
|-------------------|--------------------------------------------------------|-----------------------------------------|
| `SNS_TOPIC_ARN`   | `arn:aws:sns:eu‑north‑1:123456789012:ebs‑cleanup`      | **Required** – your SNS topic ARN       |
| `DRY_RUN`         | `true` / `false`                                       | `true` → log only, no deletions         |
| `PROTECT_TAG_KEY` | `KeepSnapshot`                                         | Optional. Snapshots with this tag key are skipped |

### 3. Attach IAM Role

```json
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
