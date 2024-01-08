class ClientAlreadyExists(Exception):

    def __init__(self, client_name, client_address):
        self._client_name = client_name
        self._client_address = client_address

    def __str__(self):
        return f"הלקוח/ה: *{self._client_name}* בכתובת: *{self._client_address}* כבר נמצא/ת ברשימת הלקוחות שלך."


class IndexIsOutOfRange(Exception):

    def __str__(self):
        return "הקלדת מספר שלא נמצא ברשימה, אנא הקלד מספר תקין."


class DebtToDeleteIsNegative(Exception):

    def __str__(self):
        return "לא ניתן להוריד חוב שמספרו שלילי, אנא הזן מספר חיובי."
