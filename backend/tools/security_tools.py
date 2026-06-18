import boto3
import logging
import json
from datetime import datetime, timedelta
from .base_tool import BaseTool
from .tool_registry import ToolRegistry

logger = logging.getLogger(__name__)

class GetGuardDutyFindingsTool(BaseTool):
    name = "get_guardduty_findings"
    description = "Retrieves active GuardDuty findings. Use this to check for active threats."
    parameters_schema = {
        "type": "object",
        "properties": {
            "aws_profile": {
                "type": "string",
                "description": "AWS profile to use"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of findings to return",
                "default": 10
            }
        }
    }

    async def execute(self, aws_profile: str = "default", max_results: int = 10) -> dict:
        try:
            session = boto3.Session(profile_name=aws_profile)
            client = session.client('guardduty')
            
            # First, get the detector ID
            detectors = client.list_detectors()
            if not detectors.get('DetectorIds'):
                return {"message": "No GuardDuty detectors found."}
                
            detector_id = detectors['DetectorIds'][0]
            
            # List finding IDs
            findings_list = client.list_findings(
                DetectorId=detector_id,
                FindingCriteria={
                    'Criterion': {
                        'service.archived': {'Eq': ['false']}
                    }
                },
                MaxResults=max_results
            )
            
            finding_ids = findings_list.get('FindingIds', [])
            if not finding_ids:
                return {"message": "No active GuardDuty findings.", "security_score": 100}
                
            # Get finding details
            findings_details = client.get_findings(
                DetectorId=detector_id,
                FindingIds=finding_ids
            )
            
            # Calculate a basic score impact based on finding severities
            max_severity = 0
            for finding in findings_details.get('Findings', []):
                severity = finding.get('Severity', 0)
                max_severity = max(max_severity, severity)
                
            score = 100 - (max_severity * 10)  # Severity 1-10 -> Score 0-100
            
            findings_dict = json.loads(json.dumps(findings_details.get('Findings', []), default=str))
            return {
                "findings": findings_dict,
                "security_score": int(score)
            }
            
        except Exception as e:
            logger.error(f"Error getting GuardDuty findings: {e}")
            return {"error": str(e)}

class GetSecurityHubFindingsTool(BaseTool):
    name = "get_securityhub_findings"
    description = "Retrieves high/critical Security Hub findings."
    parameters_schema = {
        "type": "object",
        "properties": {
            "aws_profile": {"type": "string"}
        }
    }

    async def execute(self, aws_profile: str = "default") -> dict:
        try:
            session = boto3.Session(profile_name=aws_profile)
            client = session.client('securityhub')
            
            findings = client.get_findings(
                Filters={
                    'RecordState': [{'Value': 'ACTIVE', 'Comparison': 'EQUALS'}],
                    'SeverityLabel': [{'Value': 'CRITICAL', 'Comparison': 'EQUALS'}, {'Value': 'HIGH', 'Comparison': 'EQUALS'}]
                },
                MaxResults=10
            )
            findings_dict = json.loads(json.dumps(findings.get('Findings', []), default=str))
            return {"findings": findings_dict}
        except Exception as e:
            return {"error": str(e)}


class LookupCloudTrailEventsTool(BaseTool):
    name = "lookup_cloudtrail_events"
    description = "Looks up recent CloudTrail management events."
    parameters_schema = {
        "type": "object",
        "properties": {
            "aws_profile": {"type": "string"},
            "max_results": {"type": "integer", "default": 10}
        }
    }

    async def execute(self, aws_profile: str = "default", max_results: int = 10) -> dict:
        try:
            session = boto3.Session(profile_name=aws_profile)
            client = session.client('cloudtrail')
            events = client.lookup_events(MaxResults=max_results)
            events_dict = json.loads(json.dumps(events.get('Events', []), default=str))
            return {"events": events_dict}
        except Exception as e:
            return {"error": str(e)}

class QueryCloudWatchLogsTool(BaseTool):
    name = "query_cloudwatch_logs"
    description = "Queries CloudWatch Logs for a given log group and filter pattern."
    parameters_schema = {
        "type": "object",
        "properties": {
            "aws_profile": {"type": "string"},
            "log_group_name": {"type": "string"},
            "filter_pattern": {"type": "string", "default": "ERROR"}
        },
        "required": ["log_group_name"]
    }

    async def execute(self, log_group_name: str, filter_pattern: str = "ERROR", aws_profile: str = "default") -> dict:
        try:
            session = boto3.Session(profile_name=aws_profile)
            client = session.client('logs')
            response = client.filter_log_events(
                logGroupName=log_group_name,
                filterPattern=filter_pattern,
                limit=10
            )
            events_dict = json.loads(json.dumps(response.get('events', []), default=str))
            return {"events": events_dict}
        except Exception as e:
            return {"error": str(e)}

def register_security_tools(registry: ToolRegistry):
    registry.register(GetGuardDutyFindingsTool())
    registry.register(GetSecurityHubFindingsTool())
    registry.register(LookupCloudTrailEventsTool())
    registry.register(QueryCloudWatchLogsTool())
