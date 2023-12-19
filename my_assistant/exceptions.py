class ClientAlreadyExists(Exception):

    def __init__(self, client_name):
        self._client_name = client_name

    def __str__(self):
        return f"הלקוח/ה {self._client_name} כבר נמצא/ת ברשימת הלקוחות שלך."


class IndexOfClientIsTooBig(Exception):

    def __str__(self):
        return "הקלדת מספר גדול מידיי שלא נמצא ברשימת הלקוחות, אנא הקלד מספר תקין."
