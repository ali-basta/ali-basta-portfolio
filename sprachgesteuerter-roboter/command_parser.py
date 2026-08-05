"""
Natural language to structured command.

Turns a free-form spoken instruction into JSON the rest of the pipeline can act
on. The LLM backend is swappable via the LLM_PROVIDER environment variable:
either a hosted model (OpenAI API) or a locally hosted one through Ollama. The
local model became the default in practice, since it removes the per-request
cost and keeps lab data on site.

A regex fallback runs if the model is unreachable or returns something that will
not parse. It handles the common phrasings only ("3 red", "red 3", "all blue")
in English and German — enough to keep a demo alive, not a replacement for the
model.

Example
-------
    "put 3 small green coins in the green box, then take 2 large orange ones"

    {"action": "pick",
     "items": [{"color": "green", "amount": 3, "box": "green"},
               {"color": "orange", "amount": 2}]}
"""

import base64
import json
import os
import re

import cv2

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
OPENAI_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

VALID_ORDERS = {
    "left_to_right", "right_to_left",
    "top_to_bottom", "bottom_to_top",
    "largest_first", "smallest_first",
}

SYSTEM_PROMPT = (
    "You are an assistant for a robotics project.\n"
    "Convert the user's instruction into compact JSON with this schema:\n"
    "{\n"
    '  "action": "pick",\n'
    '  "items": [ {"color":"<lowercase>", "amount": <int | "all">, '
    '"order": <optional>, "box": <optional color>}, ... ]\n'
    "}\n"
    "Rules:\n"
    "- Always set action to 'pick'.\n"
    "- Always return an 'items' array, even for a single color.\n"
    "- Colors: red, green, blue, orange.\n"
    "- If the user says 'all', amount='all'. Accept number words and digits.\n"
    "- Orders: " + " | ".join(sorted(VALID_ORDERS)) + ".\n"
    "- If the user says 'in the <color> box', set that item's \"box\".\n"
    "- Output ONLY the JSON."
)

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eins": 1, "zwei": 2, "drei": 3, "vier": 4, "fünf": 5, "fuenf": 5,
    "sechs": 6, "sieben": 7, "acht": 8, "neun": 9, "zehn": 10,
}
COLORS = ["red", "green", "blue", "orange"]
ALL_TOKENS = {"all", "alle", "alles"}

ORDER_PATTERNS = [
    (r"left\s*to\s*right|links.*(nach|to)\s*rechts", "left_to_right"),
    (r"right\s*to\s*left|rechts.*(nach|to)\s*links", "right_to_left"),
    (r"top\s*to\s*bottom|oben.*(nach|to)\s*unten",   "top_to_bottom"),
    (r"bottom\s*to\s*top|unten.*(nach|to)\s*oben",   "bottom_to_top"),
    (r"largest\s*first|biggest\s*first|größ.*zuerst", "largest_first"),
    (r"smallest\s*first|kleinst.*zuerst",             "smallest_first"),
]


def _frame_as_image_part(frame):
    """Encode a frame as a base64 image part, so the model can see the scene."""
    if frame is None:
        return []
    ok, buffer = cv2.imencode(".jpg", frame)
    if not ok:
        return []
    b64 = base64.b64encode(buffer.tobytes()).decode()
    return [{"type": "image_url",
             "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]


def instruction_to_command(user_instruction, frame=None):
    """Parse an instruction into a command dict, or None if nothing was understood."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": [{"type": "text", "text": user_instruction}]
                                    + _frame_as_image_part(frame)},
    ]

    try:
        if LLM_PROVIDER == "ollama":
            import ollama_client

            has_image = len(messages[1]["content"]) > 1
            response = (ollama_client.chat_vision(messages) if has_image
                        else ollama_client.chat_text(messages))
            raw = ollama_client.extract_text(response)
        else:
            from openai import OpenAI

            response = OpenAI().chat.completions.create(
                model=OPENAI_MODEL, messages=messages,
                max_tokens=300, temperature=0,
            )
            raw = response.choices[0].message.content.strip()

        return json.loads(raw)

    except Exception as exc:
        print(f"[LLM] falling back to regex parser: {exc}")
        return _fallback_parse(user_instruction)


def _detect_order(text):
    for pattern, value in ORDER_PATTERNS:
        if re.search(pattern, text):
            return value
    return None


def _coerce_amount(token):
    if token in ALL_TOKENS:
        return "all"
    if token in NUMBER_WORDS:
        return NUMBER_WORDS[token]
    try:
        return int(token)
    except (TypeError, ValueError):
        return 1


def _fallback_parse(user_instruction):
    """Regex parser for the common phrasings, used only when the model fails."""
    text = (user_instruction or "").lower()
    number = r"(?:\d+|" + "|".join(map(re.escape, NUMBER_WORDS)) + r"|all|alle|alles)"
    color = r"(?:" + "|".join(COLORS) + r")"

    items, consumed = [], []

    # "3 red" and "red 3"
    for pattern in (rf"\b({number})\s+({color})\b", rf"\b({color})\s+({number})\b"):
        for match in re.finditer(pattern, text):
            first, second = match.groups()
            amount, colour = (first, second) if second in COLORS else (second, first)
            order = _detect_order(text[match.end():match.end() + 120])
            items.append({"color": colour, "amount": _coerce_amount(amount),
                          **({"order": order} if order else {})})
            consumed.append(match.span())

    # Bare colour mentions not already consumed above
    wants_all = re.search(r"\b(all|alle|alles)\b", text) is not None
    for match in re.finditer(rf"\b({color})\b", text):
        if any(start <= match.start() and match.end() <= end for start, end in consumed):
            continue
        order = _detect_order(text[match.end():match.end() + 120])
        items.append({"color": match.group(1), "amount": "all" if wants_all else 1,
                      **({"order": order} if order else {})})

    if not items:
        return None

    box_match = re.search(rf"in\s+(?:the\s+)?({color})\s+box", text)
    if box_match:
        for item in items:
            item["box"] = box_match.group(1)

    return {"action": "pick", "items": items}
