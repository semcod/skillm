"""Example Python skill callable."""


def run(*args: str, input_text: str = "") -> dict:
    text = input_text or " ".join(args) or "hello from skillm"
    return {"ok": True, "output": text, "args": list(args)}
