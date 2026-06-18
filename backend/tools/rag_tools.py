import boto3
import logging
from ..config import settings
from .base_tool import BaseTool
from .tool_registry import ToolRegistry

logger = logging.getLogger(__name__)

class QueryKnowledgeBaseTool(BaseTool):
    name = "query_knowledge_base"
    description = "Searches the internal security knowledge base for best practices, standards, and guidance."
    parameters_schema = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The question or topic to search for"
            }
        },
        "required": ["query"]
    }

    async def execute(self, query: str) -> dict:
        kb_id = settings.BEDROCK_KNOWLEDGE_BASE_ID
        if not kb_id:
            return {"message": "Knowledge base is not configured (BEDROCK_KNOWLEDGE_BASE_ID is missing). Please refer to public AWS documentation instead."}
            
        try:
            client = boto3.client('bedrock-agent-runtime', region_name=settings.AWS_REGION)
            response = client.retrieve(
                knowledgeBaseId=kb_id,
                retrievalQuery={'text': query},
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': 3
                    }
                }
            )
            
            results = []
            for result in response.get('retrievalResults', []):
                results.append({
                    "content": result.get('content', {}).get('text'),
                    "score": result.get('score'),
                    "location": result.get('location', {}).get('s3Location', {}).get('uri')
                })
                
            return {"results": results}
        except Exception as e:
            logger.error(f"Error querying knowledge base: {e}")
            return {"error": str(e)}

def register_rag_tools(registry: ToolRegistry):
    registry.register(QueryKnowledgeBaseTool())
