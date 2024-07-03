import re


class RegexPatterns:
    @classmethod
    def symbol(cls, text):
        pattern = r"<[A-Z]> ::="
        return re.findall(pattern, text)

    @classmethod
    def symbol_alt(cls, text):
        pattern = r"<[A-Z]>"
        return re.findall(pattern, text)

    @classmethod
    def variable(cls, text):
        pattern = r"([a-z])<([A-Z])>"
        return re.findall(pattern, text)


patterns = RegexPatterns()
