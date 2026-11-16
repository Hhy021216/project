import random

# 命中任一关键词，即走问候短路
GREETING_KEYWORDS = [
    "你好",
    "您好",
    "hi",
    "hello",
    "你是谁",
    "您是谁",
    "你叫什么",
    "你的名字",
    "who are you",
    "在吗",
    "在不在",
    "有人吗",
]

# 随机取一条，避免每次回复完全一样
GREETING_RESPONSES = [
    "你好！我是传智教育智能助教，有什么可以帮你？",
    "传智教育智能助手已就位，小主有何吩咐？",
    "学IT就来黑马程序员，有什么可以帮你？",
]

def match_greeting(query: str):
    text = (query or "").strip().lower()
    # 去掉常见标点，兼容「在吗？」「你好！」
    for ch in "？?！!。.，,":
        text = text.replace(ch, "")
    text = text.strip()

    if text in {k.lower() for k in GREETING_KEYWORDS}:
        return random.choice(GREETING_RESPONSES)
    return None
