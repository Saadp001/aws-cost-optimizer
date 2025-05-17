import os
import boto3
from botocore.exceptions import ClientError

REGION = os.getenv("AWS_REGION", "us-east-1")
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
TAG_KEY = os.getenv("PROTECT_TAG_KEY", "KeepSnapshot")
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")

ec2 = boto3.client("ec2", region_name=REGION)
sns = boto3.client("sns", region_name=REGION)

def send_notification(message):
    if SNS_TOPIC_ARN:
        try:
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject="EBS Snapshot Cleanup Report",
                Message=message
            )
        except ClientError as e:
            print(f"Failed to send SNS notification: {e}")

def lambda_handler(event, context):
    report = []

    try:
        snapshots = ec2.describe_snapshots(OwnerIds=["self"])["Snapshots"]
        print(f"Found {len(snapshots)} snapshots")

        # Get all instance IDs that are currently running or stopped
        instance_data = ec2.describe_instances(
            Filters=[{"Name": "instance-state-name", "Values": ["running", "stopped"]}]
        )
        attached_volume_ids = set()
        for reservation in instance_data["Reservations"]:
            for instance in reservation["Instances"]:
                for mapping in instance.get("BlockDeviceMappings", []):
                    volume_id = mapping["Ebs"]["VolumeId"]
                    attached_volume_ids.add(volume_id)

        for snapshot in snapshots:
            snapshot_id = snapshot["SnapshotId"]
            snapshot_tags = {tag["Key"]: tag["Value"] for tag in snapshot.get("Tags", [])}

            if TAG_KEY in snapshot_tags:
                continue  # Skip protected snapshots

            volume_id = snapshot.get("VolumeId")

            should_delete = False
            reason = ""

            if not volume_id:
                should_delete = True
                reason = "Not associated with any volume"
            elif volume_id not in attached_volume_ids:
                try:
                    volume_info = ec2.describe_volumes(VolumeIds=[volume_id])
                    if not volume_info["Volumes"][0]["Attachments"]:
                        should_delete = True
                        reason = "Volume is detached"
                except ClientError as e:
                    if e.response["Error"]["Code"] == "InvalidVolume.NotFound":
                        should_delete = True
                        reason = "Volume no longer exists"

            if should_delete:
                if DRY_RUN:
                    report.append(f"[DRY RUN] Would delete snapshot {snapshot_id} – {reason}")
                else:
                    ec2.delete_snapshot(SnapshotId=snapshot_id)
                    report.append(f"Deleted snapshot {snapshot_id} – {reason}")
            else:
                print(f"Retaining snapshot {snapshot_id}")

    except Exception as e:
        error_message = f"Error during snapshot cleanup: {str(e)}"
        print(error_message)
        send_notification(error_message)
        raise

    if report:
        summary = "\n".join(report)
    else:
        summary = "No stale EBS snapshots found."

    print(summary)
    send_notification(summary)
