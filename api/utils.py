from django.forms.models import model_to_dict

from .models import User


def get_user_from_email(email: str):
    user = User.objects.get(email=email)

    return model_to_dict(user)

def validate_email_exists(email: str):
    try:
        user = User.objects.get(email=email)
        return True
    except User.DoesNotExist:
        return False

def validate_address_camps(cep: str, state: str, city: str, district: str, street: str, number: str):
    if cep is None or cep == "":
        return {"error": "CEP inválido!", "status": False}
    
    if state is None or state == "":
        return False

    if city is  None or city == "":
        return False

    if district is  None or district == "":
        return False

    if street is  None or street == "":
        return False

    if number is  None or number == "":
        return False

    return True
