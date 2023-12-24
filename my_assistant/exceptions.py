class ClientAlreadyExists(Exception):

    def __init__(self, client_name):
        self._client_name = client_name

    def __str__(self):
        return f"הלקוח/ה {self._client_name} כבר נמצא/ת ברשימת הלקוחות שלך."


class IndexIsOutOfRange(Exception):

    def __str__(self):
        return "הקלדת מספר שלא נמצא ברשימה, אנא הקלד מספר תקין."


class DebtToDeleteIsNegative(Exception):

    def __str__(self):
        return "לא ניתן להוריד חוב שמספרו שלילי, אנא הזן מספר חיובי."
