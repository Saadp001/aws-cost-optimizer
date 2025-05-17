import boto3
import json

# Initialize AWS clients
ec2 = boto3.client('ec2')
sns = boto3.client('sns')

# Replace with your actual SNS topic ARN
SNS_TOPIC_ARN = 'arn:aws:sns:<your-region>:<your-account-id>:ebs-cleanup-alerts'

def notify(message):
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject='EBS Snapshot Cleanup Notification',
        Message=message
    )

def lambda_handler(event, context):
    deleted_snapshots = []
    skipped_snapshots = []

    try:
        # Get all EBS snapshots owned by this account
        snapshots_response = ec2.describe_snapshots(OwnerIds=['self'])

        # Get all running EC2 instance IDs
        instances_response = ec2.describe_instances(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
        )
        active_instance_ids = {
            instance['InstanceId']
            for reservation in instances_response['Reservations']
            for instance in reservation['Instances']
        }

        for snapshot in snapshots_response['Snapshots']:
            snapshot_id = snapshot['SnapshotId']
            volume_id = snapshot.get('VolumeId')

            if not volume_id:
                # No volume associated — safe to delete
                ec2.delete_snapshot(SnapshotId=snapshot_id)
                deleted_snapshots.append(snapshot_id)
            else:
                try:
                    volume_response = ec2.describe_volumes(VolumeIds=[volume_id])
                    attachments = volume_response['Volumes'][0].get('Attachments', [])
                    if not attachments:
                        ec2.delete_snapshot(SnapshotId=snapshot_id)
                        deleted_snapshots.append(snapshot_id)
                    else:
                        skipped_snapshots.append(snapshot_id)
                except ec2.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == 'InvalidVolume.NotFound':
                        ec2.delete_snapshot(SnapshotId=snapshot_id)
                        deleted_snapshots.append(snapshot_id)
                    else:
                        skipped_snapshots.append(snapshot_id)

        message = f"""
EBS Snapshot Cleanup Report

✅ Deleted Snapshots:
{json.dumps(deleted_snapshots, indent=2)}

⏭️ Skipped Snapshots:
{json.dumps(skipped_snapshots, indent=2)}
        """

        print(message)
        notify(message.strip())

    except Exception as e:
        error_message = f"❌ Lambda function failed: {str(e)}"
        print(error_message)
        notify(error_message)

