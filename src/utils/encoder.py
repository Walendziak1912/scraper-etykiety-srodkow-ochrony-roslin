from __future__ import annotations
import base64
import binascii
from cv2 import data

def encode_base64(text: str, encoding: str = "utf-8", url_safe: bool = False) -> str:
    raw = text.encode(encoding)
    if url_safe:
        return base64.urlsafe_b64encode(raw).decode("ascii")
    return base64.b64encode(raw).decode("ascii")

def _normalize_b64(s: str) -> str:
    cleaned = ''.join(c for c in s if c.isalnum() or c in '+/=')
    padding = len(cleaned) % 4
    if padding:
        cleaned += '=' * (4 - padding)
    return "".join(cleaned.split())

def _pad_b64(s: str) -> str:
    pad = len(s) % 4
    if pad:
        return s + "=" * (4 - pad)
    return s

def decode_base64(b64: str, encoding: str = "utf-8", url_safe: bool = False) -> str:
    cleaned = _normalize_b64(b64)
    if not cleaned:
        return ""
    padded = _pad_b64(cleaned)
    try:
        if url_safe:
            raw = base64.urlsafe_b64decode(padded)
        else:
            raw = base64.b64decode(padded, validate=True)
    except (binascii.Error, ValueError) as e:
        raise ValueError("Niepoprawny ciąg Base64") from e
    return raw.decode(encoding)
