import string


class Alphabet:
    alphabet = list(string.ascii_uppercase)

    def __init__(self) -> None:
        pass

    @classmethod
    def get_next_letter(cls, last_state: str) -> str:  # Added self parameter
        # Corrected reference to class variable
        return cls.alphabet[cls.alphabet.index(last_state) + 1]

    @classmethod
    def index_to_letter(cls, index: int) -> str:  # Added self parameter
        return cls.alphabet[index]  # Corrected reference to class variable


alphabet = Alphabet()
