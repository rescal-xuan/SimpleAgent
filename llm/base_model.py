from dotenv  import load_dotenv
from openai import OpenAI
import os
load_dotenv()
from langchain_core.language_models import BaseLLM
from langchain_core.outputs import LLMResult
from typing import Optional, List, Dict, Any, Iterator
import os
from openai import OpenAI
from langchain_openai import ChatOpenAI
class LanguageModel:
    def __init__(self,model_name="deepseek-chat"):
        super().__init__()
        self.model_name=model_name
        self.api_key=os.getenv("API-KEY")
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
        self.llm =ChatOpenAI(model="deepseek-chat",api_key=self.api_key,base_url="https://api.deepseek.com")

    def generate_text(
        self, 
        prompt: List[str], 
        stop: Optional[List[str]] = None,
        **kwargs: Any
    ) -> LLMResult:
        
        response = self.client.chat.completions.create(
            model='deepseek-chat',
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": prompt},
            ],
            stream=False
        )
        
        return response.choices[0].message.content
    
    def _stream(self, prompt: str, **kwargs: Any) -> Iterator[LLMResult]:
        raise NotImplementedError("Streaming not implemented")
    
    @property
    def _llm_type(self) -> str:
        return "deepseek_langchain_wrapper"
    
    def get_llm(self):
        return self.llm
        
if  __name__ =="__main__"   :    
    agent =LanguageModel('agent')
    prompt="""分析用户意图并选择操作。可用工具：
        - calculator: 可以执行加减乘除运算

        用户输入：请将3、5、7三个数字相加

        请返回JSON格式：
        {
            "tool": "工具名" | null,
            "action": "use" | "direct_response"
        }"""
    print(agent.generate_text(prompt))

