import re


class PhoneNormalizer:
    _cleanup_pattern = re.compile(r"[\s\-()]")

    def normalize_israeli_phone(self, phone: str) -> str:
        raw = self._cleanup_pattern.sub("", phone)
        if raw.startswith("+"):
            raw = raw[1:]
        if raw.startswith("972"):
            rest = raw[3:]
            if not rest.startswith("0"):
                rest = f"0{rest}"
            raw = rest
        if not raw.startswith("0"):
            raise ValueError("Phone number must resolve to local Israeli format")
        if len(raw) not in {9, 10}:
            raise ValueError("Unsupported Israeli phone number length")
        return raw
