from .base_tool   import Tool
import requests
@Tool.register("weather")
class Weather(Tool):
    "可以执行天气查询"
    def __init__(self):
        super().__init__("天气查询")
    def _execute(self, city,*args):
        url =f"http://api.tangdouz.com/tq.php?dz={city}"
        response =requests.get(url)
        return response.text.replace(r"\r","\n")
    