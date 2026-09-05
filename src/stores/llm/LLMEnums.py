from enum import Enum

class LLMENums(Enum):
    OpenAI = 'openai' 
    CoHere = 'cohere ' 
    
class OpenAIEnums (Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class CoHereEnums(Enum):
    SYSTEM = "SYSTEM"
    USER = "USER"
    ASSISTANT = "CHATBOT"

    DOCUMENT = "search_document"
    QUERY = "search_query"

class DocumentTypeEnum(Enum):
    
    QUERY = "query" 
    DOCUMENT = "document"