import json
import logging
import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from .schemas import ChatRequest
from ..llm.bedrock_client import BedrockClient
from ..tools.tool_registry import ToolRegistry
from ..tools.iam_tools import register_iam_tools
from ..tools.policy_tools import register_policy_tools
from ..tools.audit_tools import register_audit_tools
from ..tools.security_tools import register_security_tools
from ..tools.governance_tools import register_governance_tools
from ..tools.rag_tools import register_rag_tools
from ..config import settings
import os

logger = logging.getLogger(__name__)

router = APIRouter()
bedrock = BedrockClient(region_name=settings.AWS_REGION)

# Setup CISA tools
cisa_registry = ToolRegistry()
register_iam_tools(cisa_registry)
register_policy_tools(cisa_registry)
register_audit_tools(cisa_registry)
cisa_tool_specs = cisa_registry.get_bedrock_tool_specs()

# Setup CSGA tools
csga_registry = ToolRegistry()
register_security_tools(csga_registry)
register_governance_tools(csga_registry)
register_rag_tools(csga_registry)
csga_tool_specs = csga_registry.get_bedrock_tool_specs()

# Load Company Policies (Simulating RAG Knowledge)
company_policies = ""
policy_path = os.path.join(os.path.dirname(__file__), "..", "..", "knowledge", "company_policies.md")
try:
    if os.path.exists(policy_path):
        with open(policy_path, "r", encoding="utf-8") as f:
            company_policies = f.read()
except Exception as e:
    logger.warning(f"Could not load company policies: {e}")

cisa_system_prompt_text = (
    "You are CISA (Cloud Identity Security Assistant), a Senior AWS Cloud Identity Security Engineer. "
    "You help users analyze their AWS IAM resources, identify security risks, and apply least privilege principles. "
    "Always be professional, concise, and format your output beautifully with markdown tables where appropriate. "
    "When presenting tables or usernames, always use bold formatting for resource names so they stand out clearly (e.g., **user-name**). "
    "\n\nCRITICAL RULES ABOUT TOOL USE:"
    "\n- NEVER call any tools for casual greetings, general questions, or anything unrelated to AWS resources."
    "\n- ONLY use tools when the user EXPLICITLY asks you to query or audit their AWS account (e.g., 'list users', 'run audit', 'show roles')."
    "\n- For greetings like 'hello', 'hi', 'how are you' — simply respond conversationally with NO tool calls."
    "\n- For general questions about IAM concepts — answer from your knowledge, NO tool calls needed."
)

if company_policies:
    cisa_system_prompt_text += (
        "\n\nIMPORTANT: You must evaluate all findings against the following INTERNAL COMPANY POLICIES.\n"
        f"--- INTERNAL COMPANY POLICIES ---\n{company_policies}\n---------------------------------\n"
    )

csga_system_prompt_text = (
    "You are CSGA (Cloud Security & Governance Assistant), a Senior AWS Cloud Security Engineer and Governance Consultant. "
    "You help users analyze their AWS security posture, investigate threats, and verify governance configurations. "
    "Always be professional, concise, and format your output beautifully with markdown tables where appropriate. "
    "You have access to AWS GuardDuty, Security Hub, S3, Backup, CloudTrail, CloudWatch Logs, AWS Config, and KMS, as well as a Knowledge Base for best practices. "
    "Use CloudTrail to lookup recent management events and CloudWatch Logs to search log groups for errors or patterns. "
    "If a user asks about best practices or concepts, ALWAYS use the 'query_knowledge_base' tool first."
)

async def stream_agent_response(request: ChatRequest):
    agent_type = request.agent.lower()
    
    if agent_type == "csga":
        active_registry = csga_registry
        active_tool_specs = csga_tool_specs
        system_prompt = [{"text": csga_system_prompt_text}]
    else:
        active_registry = cisa_registry
        active_tool_specs = cisa_tool_specs
        system_prompt = [{"text": cisa_system_prompt_text}]

    messages = request.conversation_history + [
        {"role": "user", "content": [{"text": request.message}]}
    ]

    iterations = 0
    while iterations < settings.MAX_TOOL_ITERATIONS:
        iterations += 1
        
        # Retry once on transient Bedrock errors
        for attempt in range(2):
            try:
                response = await asyncio.to_thread(
                    bedrock.converse_sync,
                    model_id=settings.BEDROCK_MODEL_ID,
                    messages=messages,
                    system_prompts=system_prompt,
                    tools=active_tool_specs,
                    temperature=settings.BEDROCK_TEMPERATURE
                )
                break  # success
            except Exception as e:
                if attempt == 1:
                    yield json.dumps({"type": "error", "content": f"Bedrock API error: {str(e)}"}) + "\n"
                    return
                logger.warning(f"Bedrock call failed (attempt {attempt+1}), retrying: {e}")
                await asyncio.sleep(1)
        
        assistant_message = response["output"]["message"]
        messages.append(assistant_message)
        
        stop_reason = response.get("stopReason")
        
        if stop_reason == "tool_use":
            tool_results = []
            for block in assistant_message.get("content", []):
                if "toolUse" in block:
                    tool_use = block["toolUse"]
                    tool_name = tool_use["name"]
                    tool_input = tool_use["input"]
                    tool_use_id = tool_use["toolUseId"]
                    
                    # Yield a status message to the frontend so it knows a tool is running
                    yield json.dumps({"type": "tool_status", "tool": tool_name}) + "\n"
                    
                    # Inject aws_profile if available
                    if request.aws_profile:
                        tool_input["aws_profile"] = request.aws_profile
                        
                    try:
                        result = await active_registry.execute_tool(tool_name, **tool_input)
                        # If the tool returned a security_score, stream it to the frontend
                        if isinstance(result, dict) and "security_score" in result:
                            yield json.dumps({
                                "type": "security_score",
                                "score": result["security_score"]
                            }) + "\n"
                    except Exception as e:
                        result = {"error": str(e)}
                        
                    tool_results.append({
                        "toolResult": {
                            "toolUseId": tool_use_id,
                            "content": [{"json": result}]
                        }
                    })
            
            messages.append({"role": "user", "content": tool_results})
            # Continue the loop to send results back to the LLM
        else:
            # Model finished (end_turn, max_tokens, etc.)
            final_text = ""
            for block in assistant_message.get("content", []):
                if "text" in block:
                    final_text += block["text"]
            
            # Yield final text
            yield json.dumps({"type": "message", "content": final_text}) + "\n"
            break

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    return StreamingResponse(
        stream_agent_response(request),
        media_type="application/x-ndjson"
    )

@router.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}

@router.get("/profiles")
async def list_profiles():
    """Return available AWS named profiles from the local credentials file."""
    import boto3
    try:
        profiles = boto3.session.Session().available_profiles
        return {"profiles": profiles}
    except Exception as e:
        return {"profiles": ["default"], "error": str(e)}
