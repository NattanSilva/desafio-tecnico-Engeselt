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


def validate_book_camps(
    title: str,
    author: str,
    isbn: str,
    editor: str,
    year_publication: str,
    total_quantity: str,
    available_quantity: str,
):

    response = {"status": True, "error": {}}

    if int(total_quantity) <= 0:
        response["error"][
            "total_quantity"
        ] = "*O campo quantidade total deve ser maior que zero!*"
        response["status"] = False
    if int(available_quantity) < 0:
        response["error"][
            "available_quantity"
        ] = "*O campo quantidade disponivel deve ser maior que zero!*"
        response["status"] = False
    if int(available_quantity) > int(total_quantity):
        response["error"][
            "available_quantity"
        ] = "*O campo quantidade disponivel não pode ser maior que a quantidade total!*"
        response["status"] = False
    if title is None or title == "":
        response["error"]["title"] = "*O campo titulo é obrigatório!*"
        response["status"] = False
    if author is None or author == "":
        response["error"]["author"] = "*O campo autor é obrigatório!*"
        response["status"] = False
    if isbn is None or isbn == "":
        response["error"]["isbn"] = "*O campo isbn é obrigatório!*"
        response["status"] = False
    if editor is None or editor == "":
        response["error"]["editor"] = "*O campo editora é obrigatório!*"
        response["status"] = False
    if int(year_publication) < 0:
        response["error"][
            "year_publication"
        ] = "*O campo ano de publicação deve ser maior que zero!*"
        response["status"] = False

    return response
