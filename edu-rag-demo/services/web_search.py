from serpapi import GoogleSearch

from clients.llm import LLMClient
from config import config
from logger import logger
from prompts import WEB_PROMPT


# 格式化返回结果
def _format_lines(items, max_results):
    lines = []
    for i, item in enumerate(items[:max_results], 1):
        lines.append(
            f"{i}. {item.get('title', '')}\n"
            f"   链接: {item.get('link', '')}\n"
            f"   摘要: {item.get('snippet', '')}"
        )
    return "\n\n".join(lines)


# 查询数据，并把结果拼接成字符串
def web_search(query):
    """经 SerpAPI 搜 Google，返回标题 / 链接 / 摘要文本。"""
    max_results = config.WEB_SEARCH_MAX_RESULTS
    try:
        data = GoogleSearch({
            "q": query,
            "api_key": config.SERPAPI_API_KEY,
            "num": max_results,
            "hl": "zh-cn",
            "gl": "cn",
        }).get_dict()
    except Exception as e:
        logger.error(f"联网搜索失败: {e}")
        return ""

    if data.get("error"):
        logger.error(f"SerpAPI 错误: {data['error']}")
        return ""

    results = data.get("organic_results") or []
    if not results:
        return ""
    text = _format_lines(results, max_results)

    logger.info(f"SerpAPI 返回 {min(len(results), max_results)} 条")
    return text


class WebSearchService:
    def __init__(self, llm=None):
        self.llm = llm or LLMClient()

    def generate(self, query):
        """有搜索结果则 stage=web；否则 stage=miss，交给 Pipeline 走 Fallback。"""
        context = web_search(query)
        if not context:
            return None
        
        prompt = WEB_PROMPT.format(context=context, question=query)

        return self.llm.chat([{"role": "user", "content": prompt}])
