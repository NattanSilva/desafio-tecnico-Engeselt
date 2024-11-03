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


def validate_address_camps(
    cep: str, state: str, city: str, district: str, street: str, number: str
):
    response = {"status": False, "error": {}}

    if (
        cep is not None
        or cep != ""
        or state is not None
        or state != ""
        or city is not None
        or city != ""
        or district is not None
        or district != ""
        or street is not None
        or street != ""
        or number is not None
        or number != ""
    ):
        if cep is None or cep == "":
            response["error"]["cep"] = "*O campo CEP é obrigatório!*"
            response["status"] = True
        if state is None or state == "":
            response["error"]["state"] = "O campo estado é obrigatório"
            response["status"] = True
        if city is None or city == "":
            response["error"]["city"] = "O campo cidade é obrigatório"
            response["status"] = True
        if district is None or district == "":
            response["error"]["district"] = "O campo bairro é obrigatório"
            response["status"] = True
        if street is None or street == "":
            response["error"]["street"] = "O campo rua é obrigatório"
            response["status"] = True
        if number is None or number == "":
            response["error"]["number"] = "O campo numero é obrigatório"
            response["status"] = True

        return response
