import json
import logging
from typing import Any, Dict

from .base_tool import BaseTool

logger = logging.getLogger(__name__)

class AnalyzeIAMPolicyTool(BaseTool):
    @property
    def name(self) -> str:
        return "analyze_iam_policy"

    @property
    def description(self) -> str:
        return "Analyze an IAM policy document (JSON string) for security risks like wildcards and privilege escalation."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "policy_document": {
                    "type": "string",
                    "description": "The IAM policy document as a JSON string"
                }
            },
            "required": ["policy_document"]
        }

    async def execute(self, policy_document: str, **kwargs) -> Dict[str, Any]:
        try:
            policy = json.loads(policy_document)
            findings = []
            score = 100

            statements = policy.get("Statement", [])
            if isinstance(statements, dict):
                statements = [statements]

            for idx, stmt in enumerate(statements):
                if stmt.get("Effect") == "Allow":
                    actions = stmt.get("Action", [])
                    if isinstance(actions, str):
                        actions = [actions]
                    
                    resources = stmt.get("Resource", [])
                    if isinstance(resources, str):
                        resources = [resources]

                    if "*" in actions and "*" in resources:
                        findings.append({"severity": "Critical", "description": "Full admin access (Action: *, Resource: *) detected in statement."})
                        score -= 50
                    elif "*" in actions:
                        findings.append({"severity": "High", "description": "Wildcard action (Action: *) detected in statement."})
                        score -= 20
                    elif "*" in resources:
                        findings.append({"severity": "High", "description": "Wildcard resource (Resource: *) detected. Restrict to specific ARNs."})
                        score -= 10
                    
                    for action in actions:
                        if action.lower() in ["iam:passrole", "sts:assumerole"]:
                            findings.append({"severity": "High", "description": f"Dangerous action {action} detected."})
                            score -= 15

            return {
                "findings": findings,
                "risk_score": max(0, score),
                "summary": "Policy analysis complete."
            }
        except Exception as e:
            return {"error": f"Failed to parse or analyze policy: {str(e)}"}

def register_policy_tools(registry):
    registry.register(AnalyzeIAMPolicyTool())
