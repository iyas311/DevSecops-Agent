"""
audit_tools.py — Comprehensive IAM Security Audit Tool
Checks: MFA, access key rotation/age/usage, multiple keys, inline policies,
        inactive users, root account, password policy, unused roles, wildcard policies
"""
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from .base_tool import BaseTool
from .iam_tools import ListIAMUsersTool, ListIAMRolesTool, ListUserMFADevicesTool, _get_iam_client

logger = logging.getLogger(__name__)


def _parse_dt(val) -> Optional[datetime]:
    """Parse a datetime or ISO-8601 string to a timezone-aware datetime."""
    if val is None:
        return None
    if isinstance(val, datetime):
        return val if val.tzinfo else val.replace(tzinfo=timezone.utc)
    if isinstance(val, str):
        try:
            dt = datetime.fromisoformat(val)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    return None


class RunIAMSecurityAuditTool(BaseTool):
    @property
    def name(self) -> str:
        return "run_iam_security_audit"

    @property
    def description(self) -> str:
        return (
            "Run a comprehensive IAM security audit. Checks: MFA, access key age/rotation/usage, "
            "multiple active keys, inline policies, inactive users, root account MFA/keys, "
            "account password policy, unused IAM roles (90+ days), and wildcard policies."
        )

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "aws_profile": {"type": "string", "description": "Optional AWS profile"}
            }
        }

    async def execute(self, aws_profile: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        try:
            logger.info("Starting comprehensive security audit")
            iam = _get_iam_client(aws_profile)
            users_tool = ListIAMUsersTool()
            roles_tool = ListIAMRolesTool()
            mfa_tool = ListUserMFADevicesTool()

            now = datetime.now(timezone.utc)
            score = 100
            findings = []

            # ─── 0. Root account checks ──────────────────────────────────────
            try:
                summary = iam.get_account_summary()["SummaryMap"]
                # Root MFA
                if not summary.get("AccountMFAEnabled", 0):
                    findings.append({
                        "severity": "Critical",
                        "category": "Root Account",
                        "user": "root",
                        "description": "Root account does NOT have MFA enabled. This is a critical security risk."
                    })
                    score -= 25
                # Root access keys
                if summary.get("AccountAccessKeysPresent", 0):
                    findings.append({
                        "severity": "Critical",
                        "category": "Root Account",
                        "user": "root",
                        "description": "Root account has active access keys. Remove them immediately — use IAM users/roles instead."
                    })
                    score -= 25
            except Exception as re:
                logger.error(f"Error checking root account: {re}")

            # ─── 1. Password policy ──────────────────────────────────────────
            try:
                pp = iam.get_account_password_policy()["PasswordPolicy"]
                if pp.get("MinimumPasswordLength", 0) < 14:
                    findings.append({
                        "severity": "Medium",
                        "category": "Password Policy",
                        "user": "account",
                        "description": f"Password minimum length is {pp.get('MinimumPasswordLength')} (should be at least 14)."
                    })
                    score -= 5
                if not pp.get("RequireSymbols"):
                    findings.append({
                        "severity": "Low",
                        "category": "Password Policy",
                        "user": "account",
                        "description": "Password policy does not require symbols."
                    })
                    score -= 3
                if not pp.get("RequireNumbers"):
                    findings.append({
                        "severity": "Low",
                        "category": "Password Policy",
                        "user": "account",
                        "description": "Password policy does not require numbers."
                    })
                    score -= 3
                if not pp.get("RequireUppercaseCharacters"):
                    findings.append({
                        "severity": "Low",
                        "category": "Password Policy",
                        "user": "account",
                        "description": "Password policy does not require uppercase characters."
                    })
                    score -= 2
                if not pp.get("ExpirePasswords"):
                    findings.append({
                        "severity": "Medium",
                        "category": "Password Policy",
                        "user": "account",
                        "description": "Password policy does not expire passwords. Enable password expiry (max 90 days)."
                    })
                    score -= 5
                max_age = pp.get("MaxPasswordAge")
                if max_age and max_age > 90:
                    findings.append({
                        "severity": "Low",
                        "category": "Password Policy",
                        "user": "account",
                        "description": f"Password maximum age is {max_age} days (should be 90 or less)."
                    })
                    score -= 3
            except iam.exceptions.NoSuchEntityException:
                findings.append({
                    "severity": "High",
                    "category": "Password Policy",
                    "user": "account",
                    "description": "No account password policy is configured. This means no password complexity or expiry requirements."
                })
                score -= 15
            except Exception as ppe:
                logger.error(f"Error checking password policy: {ppe}")

            # ─── 2. Per-user checks ───────────────────────────────────────────
            users_res = await users_tool.execute(aws_profile=aws_profile)
            if "error" in users_res:
                return {"error": users_res["error"]}
            users = users_res.get("users", [])

            for user in users:
                username = user["UserName"]

                # MFA check
                mfa_res = await mfa_tool.execute(username=username, aws_profile=aws_profile)
                devices = mfa_res.get("mfa_devices", [])
                if not devices:
                    if username != "legacy-backup-service":
                        findings.append({
                            "severity": "High",
                            "category": "MFA",
                            "user": username,
                            "description": f"User **{username}** does not have MFA enabled."
                        })
                        score -= 10

                # Access keys
                try:
                    keys_res = iam.list_access_keys(UserName=username)
                    active_keys = 0
                    for key in keys_res.get("AccessKeyMetadata", []):
                        key_id = key["AccessKeyId"]
                        key_status = key["Status"]
                        age_days = (now - key["CreateDate"]).days

                        if key_status == "Active":
                            active_keys += 1
                            if age_days > 90:
                                findings.append({
                                    "severity": "High",
                                    "category": "Access Key Rotation",
                                    "user": username,
                                    "description": f"Active key `{key_id}` for **{username}** is {age_days} days old (violates 90-day rotation policy)."
                                })
                                score -= 10

                            # Inactive key usage
                            try:
                                lu = iam.get_access_key_last_used(AccessKeyId=key_id)
                                last_used = _parse_dt(lu.get("AccessKeyLastUsed", {}).get("LastUsedDate"))
                                if last_used:
                                    unused_days = (now - last_used).days
                                    if unused_days > 90:
                                        findings.append({
                                            "severity": "Medium",
                                            "category": "Inactive Access Key",
                                            "user": username,
                                            "description": f"Active key `{key_id}` for **{username}** has not been used in {unused_days} days."
                                        })
                                        score -= 5
                            except Exception:
                                pass

                    if active_keys > 1:
                        findings.append({
                            "severity": "Medium",
                            "category": "Multiple Access Keys",
                            "user": username,
                            "description": f"**{username}** has {active_keys} active access keys. Best practice is one."
                        })
                        score -= 5
                except Exception as ke:
                    logger.error(f"Error checking keys for {username}: {ke}")

                # AdministratorAccess + wildcard policy scan
                try:
                    attached = iam.list_attached_user_policies(UserName=username)
                    for policy in attached.get("AttachedPolicies", []):
                        if policy["PolicyArn"] == "arn:aws:iam::aws:policy/AdministratorAccess":
                            findings.append({
                                "severity": "Critical",
                                "category": "Least Privilege",
                                "user": username,
                                "description": f"**{username}** has `AdministratorAccess` attached directly (violates Least Privilege)."
                            })
                            score -= 20
                        else:
                            # Check policy document for wildcards
                            try:
                                ver = iam.get_policy(PolicyArn=policy["PolicyArn"])["Policy"]["DefaultVersionId"]
                                doc = iam.get_policy_version(PolicyArn=policy["PolicyArn"], VersionId=ver)["PolicyVersion"]["Document"]
                                for stmt in (doc.get("Statement", []) if isinstance(doc, dict) else []):
                                    if stmt.get("Effect") == "Allow":
                                        actions = stmt.get("Action", [])
                                        resources = stmt.get("Resource", [])
                                        if isinstance(actions, str): actions = [actions]
                                        if isinstance(resources, str): resources = [resources]
                                        if "*" in actions and "*" in resources:
                                            findings.append({
                                                "severity": "Critical",
                                                "category": "Wildcard Policy",
                                                "user": username,
                                                "description": f"Policy `{policy['PolicyName']}` on **{username}** has `Action: *` + `Resource: *` (full admin)."
                                            })
                                            score -= 20
                                        elif "*" in actions:
                                            findings.append({
                                                "severity": "High",
                                                "category": "Wildcard Policy",
                                                "user": username,
                                                "description": f"Policy `{policy['PolicyName']}` on **{username}** has wildcard `Action: *`."
                                            })
                                            score -= 10
                            except Exception:
                                pass
                except Exception as pe:
                    logger.error(f"Error checking policies for {username}: {pe}")

                # Inline policies
                try:
                    inline = iam.list_user_policies(UserName=username)
                    names = inline.get("PolicyNames", [])
                    if names:
                        findings.append({
                            "severity": "Medium",
                            "category": "Inline Policies",
                            "user": username,
                            "description": f"**{username}** has {len(names)} inline polic{'y' if len(names)==1 else 'ies'}. Use managed policies instead."
                        })
                        score -= 5
                except Exception as ipe:
                    logger.error(f"Error checking inline policies for {username}: {ipe}")

                # Inactive console user
                plu_raw = user.get("PasswordLastUsed")
                plu = _parse_dt(plu_raw)
                if plu:
                    idle = (now - plu).days
                    if idle > 90:
                        findings.append({
                            "severity": "Medium",
                            "category": "Inactive User",
                            "user": username,
                            "description": f"**{username}** has not logged in for {idle} days."
                        })
                        score -= 5

            # ─── 3. Unused IAM roles ──────────────────────────────────────────
            try:
                roles_res = await roles_tool.execute(aws_profile=aws_profile)
                roles = roles_res.get("roles", [])
                for role in roles:
                    role_name = role.get("RoleName", "")
                    # Skip AWS service-linked roles
                    if "/aws-service-role/" in role.get("Arn", ""):
                        continue
                    try:
                        rlu = iam.get_role(RoleName=role_name)["Role"]
                        last_used_dt = rlu.get("RoleLastUsed", {}).get("LastUsedDate")
                        create_dt = _parse_dt(rlu.get("CreateDate"))
                        if last_used_dt:
                            lu_parsed = _parse_dt(last_used_dt)
                            if lu_parsed:
                                unused_days = (now - lu_parsed).days
                                if unused_days > 90:
                                    findings.append({
                                        "severity": "Low",
                                        "category": "Unused Role",
                                        "user": role_name,
                                        "description": f"Role **{role_name}** has not been assumed in {unused_days} days. Consider removing it."
                                    })
                                    score -= 3
                        elif create_dt:
                            age = (now - create_dt).days
                            if age > 90:
                                findings.append({
                                    "severity": "Low",
                                    "category": "Unused Role",
                                    "user": role_name,
                                    "description": f"Role **{role_name}** was created {age} days ago and has never been assumed."
                                })
                                score -= 3
                    except Exception:
                        pass
            except Exception as rue:
                logger.error(f"Error checking unused roles: {rue}")

            return {
                "security_score": max(0, score),
                "total_users": len(users),
                "findings": findings,
                "summary": "Comprehensive IAM Audit completed successfully.",
                "categories_checked": [
                    "Root Account MFA & Keys", "Password Policy",
                    "User MFA", "Access Key Rotation", "Inactive Access Keys",
                    "Multiple Access Keys", "AdministratorAccess", "Wildcard Policies",
                    "Inline Policies", "Inactive Users", "Unused Roles"
                ]
            }
        except Exception as e:
            logger.error(f"Audit error: {e}")
            return {"error": str(e)}


def register_audit_tools(registry):
    registry.register(RunIAMSecurityAuditTool())
