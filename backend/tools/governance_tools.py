import json
import boto3
import logging
from .base_tool import BaseTool
from .tool_registry import ToolRegistry

logger = logging.getLogger(__name__)

class ListPublicS3BucketsTool(BaseTool):
    name = "list_public_s3_buckets"
    description = "Finds S3 buckets with public access block disabled or public policies."
    parameters_schema = {
        "type": "object",
        "properties": {
            "aws_profile": {"type": "string"}
        }
    }

    async def execute(self, aws_profile: str = "default") -> dict:
        try:
            session = boto3.Session(profile_name=aws_profile if aws_profile != 'default' else None)
            s3_client = session.client('s3')
            
            buckets = s3_client.list_buckets().get('Buckets', [])
            public_buckets = []
            
            for bucket in buckets:
                bucket_name = bucket['Name']
                is_public = False
                
                try:
                    pab = s3_client.get_public_access_block(Bucket=bucket_name)
                    conf = pab.get('PublicAccessBlockConfiguration', {})
                    if not (conf.get('BlockPublicAcls') and conf.get('IgnorePublicAcls') and 
                            conf.get('BlockPublicPolicy') and conf.get('RestrictPublicBuckets')):
                        is_public = True
                except s3_client.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == 'NoSuchPublicAccessBlockConfiguration':
                        is_public = True
                
                if is_public:
                    public_buckets.append(bucket_name)
                    
            return {"public_buckets": public_buckets, "total_buckets": len(buckets)}
            
        except Exception as e:
            return {"error": str(e)}

class CheckBackupStatusTool(BaseTool):
    name = "check_backup_status"
    description = "Checks if AWS Backup vaults and plans exist."
    parameters_schema = {
        "type": "object",
        "properties": {
            "aws_profile": {"type": "string"}
        }
    }

    async def execute(self, aws_profile: str = "default") -> dict:
        try:
            session = boto3.Session(profile_name=aws_profile if aws_profile != 'default' else None)
            client = session.client('backup')
            
            vaults = client.list_backup_vaults().get('BackupVaultList', [])
            plans = client.list_backup_plans().get('BackupPlansList', [])
            
            return {
                "vaults_count": len(vaults),
                "plans_count": len(plans),
                "has_backups": len(vaults) > 0 and len(plans) > 0
            }
        except Exception as e:
            return {"error": str(e)}


class CheckKMSConfigurationTool(BaseTool):
    name = "check_kms_configuration"
    description = "Checks KMS keys to see if key rotation is enabled."
    parameters_schema = {
        "type": "object",
        "properties": {
            "aws_profile": {"type": "string"}
        }
    }

    async def execute(self, aws_profile: str = "default") -> dict:
        try:
            session = boto3.Session(profile_name=aws_profile if aws_profile != 'default' else None)
            client = session.client('kms')
            keys = client.list_keys(Limit=10).get('Keys', [])
            results = []
            for k in keys:
                key_id = k['KeyId']
                try:
                    rotation = client.get_key_rotation_status(KeyId=key_id)
                    results.append({"KeyId": key_id, "KeyRotationEnabled": rotation.get('KeyRotationEnabled')})
                except Exception:
                    pass
            kms_dict = json.loads(json.dumps(results, default=str))
            return {"kms_keys": kms_dict}
        except Exception as e:
            return {"error": str(e)}

class GetConfigComplianceTool(BaseTool):
    name = "get_config_compliance"
    description = "Gets non-compliant AWS Config rules."
    parameters_schema = {
        "type": "object",
        "properties": {
            "aws_profile": {"type": "string"}
        }
    }

    async def execute(self, aws_profile: str = "default") -> dict:
        try:
            session = boto3.Session(profile_name=aws_profile if aws_profile != 'default' else None)
            client = session.client('config')
            response = client.describe_compliance_by_config_rule(
                ComplianceTypes=['NON_COMPLIANT']
            )
            rules_dict = json.loads(json.dumps(response.get('ComplianceByConfigRules', []), default=str))
            return {"non_compliant_rules": rules_dict}
        except Exception as e:
            return {"error": str(e)}

def register_governance_tools(registry: ToolRegistry):
    registry.register(ListPublicS3BucketsTool())
    registry.register(CheckBackupStatusTool())
    registry.register(CheckKMSConfigurationTool())
    registry.register(GetConfigComplianceTool())
