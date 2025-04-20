from dotenv  import load_dotenv
from openai import OpenAI
import os
import re
load_dotenv()
api_key=os.getenv("API-KEY")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
prompt="""
 请分析用户意图并选择操作。可用工具：
        - calculator: 可以执行加减乘除运算

        用户输入：请查询北京的天气

        请返回JSON格式：
        {
            "tool": "工具名" | null,
            "action": "use" | "direct_response"
            "params":"参数"|null
        }

"""
response = client.chat.completions.create(
                model='deepseek-chat',
                messages=[
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": prompt},
                ],
                stream=False
            )
        
result =response.choices[0].message.content
pattern = r'\{[\s\n]*"tool":\s*"[^"]*",[\s\n]*"action":\s*"[^"]*",[\s\n]*"params":\s*"[^"]*"[\s\n]*\}'
match = re.search(pattern, result)
result=match.group()
print(result)