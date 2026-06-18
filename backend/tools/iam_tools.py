"""
iam_tools.py – Tools for retrieving information from AWS IAM.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError

from .base_tool import BaseTool

logger = logging.getLogger(__name__)


def _get_iam_client(aws_profile: Optional[str] = None):
    """Helper to get a boto3 IAM client with an optional profile."""
    if aws_profile:
        session = boto3.Session(profile_name=aws_profile)
        return session.client("iam")
    return boto3.client("iam")


def _format_datetime(obj: Any) -> Any:
    """Helper to format datetime objects in boto3 responses."""
    if isinstance(obj, dict):
        return {k: _format_datetime(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_format_datetime(i) for i in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    return obj


class ListIAMUsersTool(BaseTool):
    @property
    def name(self) -> str:
        return "list_iam_users"

    @property
    def description(self) -> str:
        return "List all IAM users in the AWS account. Includes metadata like ARN and Creation Date."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "aws_profile": {
                    "type": "string",
                    "description": "Optional AWS profile name to use."
                }
            }
        }

    async def execute(self, aws_profile: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        try:
            iam = _get_iam_client(aws_profile)
            paginator = iam.get_paginator("list_users")
            users = []
            for page in paginator.paginate():
                for user in page.get("Users", []):
                    users.append({
                        "UserName": user.get("UserName"),
                        "Arn": user.get("Arn"),
                        "CreateDate": user.get("CreateDate"),
                        "PasswordLastUsed": user.get("PasswordLastUsed"),
                    })
            return {"users": _format_datetime(users)}
        except Exception as e:
            logger.error("Error in list_iam_users: %s", str(e))
            return {"error": str(e)}


class GetIAMUserTool(BaseTool):
    @property
    def name(self) -> str:
        return "get_iam_user"

    @property
    def description(self) -> str:
        return "Get detailed information about a specific IAM user."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "The IAM username"},
                "aws_profile": {"type": "string", "description": "Optional AWS profile name"}
            },
            "required": ["username"]
        }

    async def execute(self, username: str, aws_profile: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        try:
            iam = _get_iam_client(aws_profile)
            response = iam.get_user(UserName=username)
            return {"user": _format_datetime(response.get("User", {}))}
        except Exception as e:
            return {"error": str(e)}


class ListIAMRolesTool(BaseTool):
    @property
    def name(self) -> str:
        return "list_iam_roles"

    @property
    def description(self) -> str:
        return "List all IAM roles in the AWS account. Includes RoleName, Arn, CreateDate, and AssumeRolePolicyDocument (trust policy) for all roles."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "aws_profile": {"type": "string", "description": "Optional AWS profile name"}
            }
        }

    async def execute(self, aws_profile: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        try:
            iam = _get_iam_client(aws_profile)
            paginator = iam.get_paginator("list_roles")
            roles = []
            for page in paginator.paginate():
                for role in page.get("Roles", []):
                    roles.append({
                        "RoleName": role.get("RoleName"),
                        "Arn": role.get("Arn"),
                        "CreateDate": role.get("CreateDate"),
                        "AssumeRolePolicyDocument": role.get("AssumeRolePolicyDocument"),
                    })
            return {"roles": _format_datetime(roles)}
        except Exception as e:
            return {"error": str(e)}


class GetIAMRoleTool(BaseTool):
    @property
    def name(self) -> str:
        return "get_iam_role"

    @property
    def description(self) -> str:
        return "Get detailed information about a specific IAM role, including its trust policy (AssumeRolePolicyDocument)."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "role_name": {"type": "string", "description": "The IAM role name"},
                "aws_profile": {"type": "string", "description": "Optional AWS profile name"}
            },
            "required": ["role_name"]
        }

    async def execute(self, role_name: str, aws_profile: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        try:
            iam = _get_iam_client(aws_profile)
            response = iam.get_role(RoleName=role_name)
            return {"role": _format_datetime(response.get("Role", {}))}
        except Exception as e:
            return {"error": str(e)}


class ListUserMFADevicesTool(BaseTool):
    @property
    def name(self) -> str:
        return "list_user_mfa_devices"

    @property
    def description(self) -> str:
        return "List MFA devices configured for a specific IAM user. Useful for checking if a user has MFA enabled."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "The IAM username"},
                "aws_profile": {"type": "string", "description": "Optional AWS profile name"}
            },
            "required": ["username"]
        }

    async def execute(self, username: str, aws_profile: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        try:
            iam = _get_iam_client(aws_profile)
            response = iam.list_mfa_devices(UserName=username)
            return {"mfa_devices": _format_datetime(response.get("MFADevices", []))}
        except Exception as e:
            return {"error": str(e)}


# A helper to register all tools easily
def register_iam_tools(registry):
    registry.register(ListIAMUsersTool())
    registry.register(GetIAMUserTool())
    registry.register(ListIAMRolesTool())
    registry.register(GetIAMRoleTool())
    registry.register(ListUserMFADevicesTool())
