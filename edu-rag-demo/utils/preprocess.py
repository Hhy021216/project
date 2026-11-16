import jieba
from pathlib import Path

def _get_stopwords():
    stopwords_path = Path(__file__).parent / "../storage/data/cn_stopwords.txt"
    with open(stopwords_path, "r", encoding="utf-8") as f:
        return set(f.read().splitlines())

STOPWORDS = _get_stopwords()


def preprocess_text(text: str):
    text = text.lower()
    return [word for word in jieba.lcut(text) if word not in STOPWORDS and word.strip()]


if __name__ == "__main__":
    print(preprocess_text("你好，我是小明，很高兴认识你"))
