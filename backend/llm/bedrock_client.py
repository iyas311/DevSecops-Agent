import json
import logging
from typing import Any, Dict, List

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class BedrockClient:
    """Client for interacting with Amazon Bedrock via the Converse API."""
    
    def __init__(self, region_name: str = "us-east-1"):
        # Use a session without a named profile so it automatically falls back to:
        # 1. Environment variables (AWS_ACCESS_KEY_ID etc.)
        # 2. EC2 Instance Metadata Service (IAM Role) when running on AWS
        # 3. ~/.aws/credentials only if available (local dev)
        session = boto3.Session(region_name=region_name)
        self.client = session.client("bedrock-runtime")

    async def converse_stream(
        self,
        model_id: str,
        messages: List[Dict[str, Any]],
        system_prompts: List[Dict[str, str]] = None,
        tools: List[Dict[str, Any]] = None,
        temperature: float = 0.3,
        max_tokens: int = 4096
    ):
        """Yield text chunks and tool use requests from the Bedrock streaming API."""
        kwargs = {
            "modelId": model_id,
            "messages": messages,
            "inferenceConfig": {
                "temperature": temperature,
                "maxTokens": max_tokens
            }
        }
        
        if system_prompts:
            kwargs["system"] = system_prompts
            
        if tools:
            kwargs["toolConfig"] = {"tools": tools}

        try:
            response = self.client.converse_stream(**kwargs)
            
            # Since this is a simple demo, we will yield events
            # The router layer will handle executing tools and managing the loop
            for event in response.get("stream", []):
                yield event

        except ClientError as e:
            logger.error("Bedrock ClientError: %s", str(e))
            yield {"error": str(e)}
        except Exception as e:
            logger.error("Bedrock Exception: %s", str(e))
            yield {"error": str(e)}

    def converse_sync(
        self,
        model_id: str,
        messages: List[Dict[str, Any]],
        system_prompts: List[Dict[str, str]] = None,
        tools: List[Dict[str, Any]] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """Synchronous converse API call (useful for tool-execution loops)."""
        kwargs = {
            "modelId": model_id,
            "messages": messages,
            "inferenceConfig": {"temperature": temperature}
        }
        if system_prompts:
            kwargs["system"] = system_prompts
        if tools:
            kwargs["toolConfig"] = {"tools": tools}

        response = self.client.converse(**kwargs)
        return response
