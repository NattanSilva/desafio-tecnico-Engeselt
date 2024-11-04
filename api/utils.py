from datetime import date
from uuid import UUID

from django.forms.models import model_to_dict

from .models import Book, Loan, User
from .serializers import BookSerializer, UserSerializer


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

    loans_by_isbn = Loan.objects.filter(isbn=isbn)

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

    if len(loans_by_isbn) > 0:
        response["error"]["isbn"] = "*Este ISBN ja foi utilizado!*"
        response["status"] = False

    return response


def get_book_by_title(title: str):
    try:
        book = Book.objects.get(title__icontains=title)

        return model_to_dict(book)
    except Book.DoesNotExist:
        return None


def get_many_books_by_title(title: str):
    result = []

    if title is None or title == "":
        books = Book.objects.filter(is_active=True, available_quantity__gt=0)

        for book in books:
            result.append(model_to_dict(book))

        return result

    books = Book.objects.filter(
        title__icontains=title, is_active=True, available_quantity__gt=0
    )

    for book in books:
        result.append(model_to_dict(book))

    return result


def get_book_by_id(book_id: str):
    try:
        book = Book.objects.get(id=book_id)

        return model_to_dict(book)
    except Book.DoesNotExist:
        return None


def validate_gt_loan_date(inicial_date: str, final_date: str):
    if str(final_date) < str(inicial_date):
        return False
    return True


def get_loan_by_id(loan_id: str):
    try:
        loan = Loan.objects.get(id=loan_id)

        return model_to_dict(loan)
    except Loan.DoesNotExist:
        return None


def get_all_users():
    users = User.objects.all()
    user_serializer = UserSerializer(data=users, many=True)
    user_serializer.is_valid()

    return user_serializer.data


def get_all_active_books():
    books = Book.objects.filter(available_quantity__gt=0, is_active=True)
    book_serializer = BookSerializer(data=books, many=True)
    book_serializer.is_valid()

    return book_serializer.data


def validate_loan_regist_camps(
    user: str, book: str, aproved_date: str, expected_devolution_date: str, status: str
):
    response = {"status": True, "error": {}}

    loans_per_user = Loan.objects.filter(user=user, book=book, status=status)

    if (status == "em aberto" or status == "pendente") and loans_per_user.exists():

        response["error"][
            "book"
        ] = "*O usário ja tem um emprestimo para este livro em aberto!*"
        response["status"] = False

    if not validate_gt_loan_date(
        date.today().strftime("%Y-%m-%d"), expected_devolution_date
    ):
        response["error"][
            "expected_devolution_date"
        ] = "*A data de devolução prevista deve ser maior que a data atual!*"
        response["status"] = False

    if not validate_gt_loan_date(aproved_date, expected_devolution_date):
        response["error"][
            "expected_devolution_date"
        ] = "*A data de devolução prevista deve ser maior que a data de emprestimo!*"
        response["status"] = False

    if not validate_gt_loan_date(date.today().strftime("%Y-%m-%d"), aproved_date):
        response["error"][
            "aproved_date"
        ] = "*A data de emprestimo deve ser maior ou igual a data atual!*"
        response["status"] = False

    return response


def format_loans_to_tempalte(loans):
    result = []

    for item in loans:
        formated_data = {}
        # convete string para UUID
        book_id = UUID(str(item.book))
        current_book = Book.objects.get(id=book_id)

        current_user = User.objects.get(email=item.user)

        formated_data["id"] = item.id
        formated_data["book_title"] = current_book.title
        formated_data["aproved_date"] = item.aproved_date
        formated_data["expected_devolution_date"] = item.expected_devolution_date
        formated_data["devolution_date"] = item.devolution_date
        formated_data["status"] = item.status
        formated_data["user_name"] = current_user.complete_name

        result.append(formated_data)

    return result


def get_loans_by_period(start_date: str, end_date: str, user: str = None):
    if user is not None and user != "":
        loans = Loan.objects.filter(
            aproved_date__range=[start_date, end_date], user=user
        )
    else:
        loans = Loan.objects.filter(aproved_date__range=[start_date, end_date])
    return format_loans_to_tempalte(loans)


def get_oppening_loans():
    loans = Loan.objects.filter(status="em aberto")
    return format_loans_to_tempalte(loans)


def devolution_validate_camps(loan_id: str, devolution_date: str):
    result = {"status": True, "error": {}}

    if loan_id == "Nenhum Emprestimo Cadastrado":
        result["error"]["loan_id"] = "*Emprestimo inexistente!*"
        result["status"] = False

        return result

    loan = Loan.objects.get(id=loan_id)

    if not validate_gt_loan_date(loan.aproved_date, devolution_date):
        result["error"][
            "devolution_date"
        ] = "*A data de devolução deve ser maior que a data de emprestimo!*"
        result["status"] = False

    return result
