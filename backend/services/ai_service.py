import json
import urllib.request
import urllib.error

DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_API_KEY = "sk-29c08aca0b664c3cbefef1d2c91326b4"


def call_deepseek(prompt: str, system: str = "") -> str:
    """Call DeepSeek API and return response text."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    }
    body = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 1024,
    }
    req = urllib.request.Request(
        DEEPSEEK_URL,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        return f"AI 服务错误: {err}"


def check_sentence(word: str, sentence: str) -> dict:
    """Check if the sentence correctly uses the given word, and evaluate grammar."""
    system = "你是一名英语老师。请用中文回复。"
    prompt = f"""请检查以下句子中单词 "{word}" 的使用是否正确，以及语法是否正确。

句子："{sentence}"

请从以下几个方面分析：
1. 单词 "{word}" 在句子中的用法是否正确
2. 语法是否正确
3. 如果正确，请给予鼓励；如果有问题，请指出并给出修改建议
4. 最后给出一个评分（1-10分）

请用简洁的格式回复，不要超过150字。"""
    result = call_deepseek(prompt, system)
    return {"word": word, "sentence": sentence, "feedback": result}
