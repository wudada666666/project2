import json
import urllib.error
import urllib.request


DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"


def call_deepseek(prompt: str, api_key: str, system: str = "") -> str:
    if not api_key or not api_key.strip():
        raise ValueError("请先填写 DeepSeek API Key")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key.strip()}",
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
        if e.code in (401, 403):
            raise ValueError("API Key 无效或已过期，请检查后重试")
        return f"AI 服务错误: {err}"


def check_sentence(word: str, sentence: str, api_key: str) -> dict:
    system = "你是一名英语老师。请用中文回复。"
    prompt = f"""请检查以下句子中单词 "{word}" 的使用是否正确，以及语法是否正确。

句子："{sentence}"

请从以下几个方面分析：
1. 单词 "{word}" 在句子中的用法是否正确
2. 语法是否正确
3. 如果正确，请给予鼓励；如果有问题，请指出并给出修改建议
4. 最后给出一个评分（1-10分）

请用简洁的格式回复，不要超过150字。"""
    result = call_deepseek(prompt, api_key, system)
    return {"word": word, "sentence": sentence, "feedback": result}
