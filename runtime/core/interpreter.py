import unicodedata


def detect_intent(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(text).lower())
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    if any(trigger in normalized for trigger in ("otworz", "uruchom", "wlacz")):
        return "OPEN_APP"
    return "UNKNOWN"
