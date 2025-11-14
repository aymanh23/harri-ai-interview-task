import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List, Optional
from app.settings import settings
from app.llm.system_instruction import system_instruction
from app.llm.user_prompt import user_prompt_template

load_dotenv()

class Citation(BaseModel): 
    source: str 
    section: Optional[str] = None 

class LLMResponseModel(BaseModel): 
    answer: str 
    citations: List[Citation]

class LLM:
    def __init__(self):
        
        self.generation_config = types.GenerateContentConfig(
            temperature=0.1,
            top_p=0.9,
            top_k=40,
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=LLMResponseModel.model_json_schema()
        )
                
        self.client = genai.Client()

        
        self.session = self.client.chats.create(
            model="gemini-2.5-flash-lite",
            config=self.generation_config,
            history=[],
        )    


    def generate(self, query:str, intents:list, retrievals:list)-> LLMResponseModel:

        # build the prompt from jinja template
        prompt = user_prompt_template.render(
            query=query,
            intents=intents,
            retrievals=retrievals
        )
        # send the prompt to the gemini and get the response
        response = self.session.send_message(prompt)

        print(response.text)
        # validate response

        try: 
            result = LLMResponseModel.model_validate_json(response.text)
        except Exception:
            result = LLMResponseModel(answer=response.text, citations=[])
        
        return result


