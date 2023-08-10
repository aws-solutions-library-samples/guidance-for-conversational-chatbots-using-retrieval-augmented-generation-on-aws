from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    DYNAMODB_TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']
    KENDRA_INDEX = os.environ['KENDRA_INDEX']
    KENDRA_REGION = os.environ['KENDRA_REGION']
    MODEL_ENDPOINT = os.environ['MODEL_ENDPOINT']
    API_KEYS_ANTHROPIC_NAME =os.environ['API_KEYS_ANTHROPIC_NAME']
    
config = Config()
