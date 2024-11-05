from datetime import datetime, timedelta

from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from rest_framework.serializers import ValidationError

from .models import Book, Loan, User
from .serializers import (
    AddressSerializer,
    BookSerializer,
    LoanSerializer,
    UserSerializer,
)
from .utils import (
    devolution_validate_camps,
    format_loans_to_tempalte,
    formated_book_list,
    get_all_active_books,
    get_all_users,
    get_loans_by_period,
    get_many_books_by_title,
    get_oppening_loans,
    get_user_from_email,
    validate_address_camps,
    validate_book_camps,
    validate_email_exists,
    validate_loan_regist_camps,
)


# Create your views here.
def login(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            django_login(request, user)
            return redirect("home")
        else:
            return render(
                request, "login.html", {"error": "*Usuário ou senha inválidos!*"}
            )

    else:
        return render(request, "login.html", {})


def logout(request):
    django_logout(request)
    return redirect("login")


@login_required
def home(request):
    if not request.user.is_authenticated:
        return redirect("/")

    user = get_user_from_email(request.user)

    if user["account_type"] == "leitor":
        active_books = Book.objects.filter(available_quantity__gt=0, is_active=True)
        book_serializer = BookSerializer(data=active_books, many=True)
        book_serializer.is_valid()

        books_list = book_serializer.data
        formated_books_list = formated_book_list(books_list, user["email"])

        if request.method == "POST" and (
            request.POST.get("book_id") is not None
            and request.POST.get("book_id") != ""
        ):
            book_id = request.POST.get("book_id")

            expected_devolution_date = datetime.now() + timedelta(days=3)

            formated_expected_devolution_date = (
                expected_devolution_date.date().strftime("%Y-%m-%d")
            )

            user_queryset = User.objects.get(email=user["email"])

            try:
                loan_serializer = LoanSerializer(
                    data={
                        "user": user_queryset.id,
                        "book": book_id,
                        "status": "pendente",
                        "expected_devolution_date": formated_expected_devolution_date,
                    }
                )

                loan_serializer.is_valid(raise_exception=True)

                loan_serializer.save()

                formated_books_list = formated_book_list(books_list, user["email"])

                return render(
                    request,
                    "home.html",
                    {
                        "user": get_user_from_email(request.user),
                        "icon": get_user_from_email(request.user)["complete_name"][0],
                        "items": formated_books_list,
                    },
                )
            except ValidationError as e:
                request.session["mensagem"] = e.detail
                request.session["error_type"] = "Solicitação de Empréstimo"
                return redirect("error")

        if request.method == "POST":
            book_name = (
                request.POST.get("search_book_name")
                if request.POST.get("search_book_name")
                else ""
            )

            filtered_books = get_many_books_by_title(book_name)
            formated_filtered_books = formated_book_list(filtered_books, user["email"])

            if filtered_books is not None:
                return render(
                    request,
                    "home.html",
                    {
                        "user": get_user_from_email(request.user),
                        "icon": get_user_from_email(request.user)["complete_name"][0],
                        "items": formated_filtered_books,
                        "saved_data": {"search_book_name": book_name},
                        "reset_button": True,
                    },
                )
            else:
                return render(
                    request,
                    "home.html",
                    {
                        "user": get_user_from_email(request.user),
                        "icon": get_user_from_email(request.user)["complete_name"][0],
                        "items": [],
                        "saved_data": {"search_book_name": book_name},
                        "reset_button": True,
                    },
                )

        return render(
            request,
            "home.html",
            {
                "user": get_user_from_email(request.user),
                "icon": get_user_from_email(request.user)["complete_name"][0],
                "items": formated_books_list,
            },
        )

    return render(
        request,
        "home.html",
        {
            "user": get_user_from_email(request.user),
            "icon": get_user_from_email(request.user)["complete_name"][0],
        },
    )


@login_required
def regist_user(request):
    if not request.user.is_authenticated:
        return redirect("/")

    if not request.user.is_superuser:
        return redirect("/home")

    if request.method == "POST":
        # Campos de registro de usuário
        complate_name = request.POST.get("complete_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        account_type = request.POST.get("account_type")
        phone = request.POST.get("phone")

        # Campos de registro de endereço
        cep = request.POST.get("cep")
        state = request.POST.get("state")
        city = request.POST.get("city")
        district = request.POST.get("district")
        street = request.POST.get("street")
        number = request.POST.get("number")
        complement = request.POST.get("complement")

        if password != confirm_password:
            return render(
                request,
                "regist_user.html",
                {
                    "user": get_user_from_email(request.user),
                    "icon": get_user_from_email(request.user)["complete_name"][0],
                    "error": {"confirm_password": "*As senhas devem ser iguais!*"},
                    "saved_data": {
                        "complete_name": complate_name,
                        "email": email,
                        "password": password,
                        "confirm_password": confirm_password,
                        "account_type": account_type,
                        "phone": phone if phone is not None or phone != "" else "",
                    },
                },
            )

        if phone is not None and phone != "" and len(phone) < 15:
            return render(
                request,
                "regist_user.html",
                {
                    "user": get_user_from_email(request.user),
                    "icon": get_user_from_email(request.user)["complete_name"][0],
                    "error": {"phone": "*Dever ser um telefone valido!*"},
                    "saved_data": {
                        "complete_name": complate_name,
                        "email": email,
                        "password": password,
                        "confirm_password": confirm_password,
                        "account_type": account_type,
                        "phone": phone if phone is not None or phone != "" else "",
                    },
                },
            )

        if validate_email_exists(email):
            return render(
                request,
                "regist_user.html",
                {
                    "user": get_user_from_email(request.user),
                    "icon": get_user_from_email(request.user)["complete_name"][0],
                    "error": {"email": "*Email ja existe!*"},
                    "saved_data": {
                        "complete_name": complate_name,
                        "email": email,
                        "password": password,
                        "confirm_password": confirm_password,
                        "account_type": account_type,
                        "phone": (phone if phone is not None or phone != "" else ""),
                    },
                },
            )
        else:
            address_validation = validate_address_camps(
                cep, state, city, district, street, number
            )

            if address_validation["status"]:
                return render(
                    request,
                    "regist_user.html",
                    {
                        "user": get_user_from_email(request.user),
                        "icon": get_user_from_email(request.user)["complete_name"][0],
                        "error": address_validation["error"],
                        "saved_data": {
                            "complete_name": complate_name,
                            "email": email,
                            "password": password,
                            "confirm_password": confirm_password,
                            "account_type": account_type,
                            "phone": phone if phone is not None or phone != "" else "",
                            "cep": cep,
                            "state": state,
                            "city": city,
                            "district": district,
                            "street": street,
                            "number": number,
                            "complement": complement,
                        },
                    },
                )
            else:
                try:
                    serializer = UserSerializer(
                        data={
                            "complete_name": complate_name,
                            "email": email,
                            "password": password,
                            "account_type": account_type,
                            "phone": None if phone is None or phone == "" else phone,
                        }
                    )

                    serializer.is_valid(raise_exception=True)
                    serializer.save()

                    address_serializer = AddressSerializer(
                        data={
                            "cep": cep,
                            "state": state,
                            "city": city,
                            "district": district,
                            "street": street,
                            "number": number,
                            "complement": complement,
                            "owner": serializer.data["id"],
                        }
                    )

                    address_serializer.is_valid(raise_exception=True)
                    address_serializer.save()

                    request.session["mensagem"] = "Novo Usário Cadastrado com Sucesso!"
                    return redirect("success")

                except ValidationError as e:
                    request.session["mensagem"] = e.detail
                    request.session["error_type"] = "Registro de Usuário"
                    return redirect("error")
    return render(
        request,
        "regist_user.html",
        {
            "user": get_user_from_email(request.user),
            "icon": get_user_from_email(request.user)["complete_name"][0],
        },
    )


@login_required
def regist_book(request):
    if not request.user.is_authenticated:
        return redirect("/")

    if not request.user.is_superuser:
        return redirect("/home")

    if request.method == "POST":
        # Buscandao dados para o registro do novo livro
        title = request.POST.get("title")
        author = request.POST.get("author")
        isbn = request.POST.get("isbn")
        editor = request.POST.get("editor")
        year_publication = request.POST.get("year_publication")
        gender = request.POST.get("gender")
        total_quantity = request.POST.get("total_quantity")
        available_quantity = request.POST.get("available_quantity")
        description = request.POST.get("description")

        book_camps_validation = validate_book_camps(
            title,
            author,
            isbn,
            editor,
            year_publication,
            total_quantity,
            available_quantity,
        )

        if not book_camps_validation["status"]:

            return render(
                request,
                "regist_book.html",
                {
                    "user": get_user_from_email(request.user),
                    "icon": get_user_from_email(request.user)["complete_name"][0],
                    "saved_data": {
                        "title": title,
                        "author": author,
                        "isbn": isbn,
                        "editor": editor,
                        "year_publication": year_publication,
                        "gender": gender,
                        "total_quantity": total_quantity,
                        "available_quantity": available_quantity,
                        "description": description,
                    },
                    "error": book_camps_validation["error"],
                },
            )
        else:
            try:
                book_serializer = BookSerializer(
                    data={
                        "title": title,
                        "author": author,
                        "isbn": isbn,
                        "editor": editor,
                        "year_publication": year_publication,
                        "gender": gender,
                        "total_quantity": total_quantity,
                        "available_quantity": available_quantity,
                        "description": description,
                    }
                )
                book_serializer.is_valid(raise_exception=True)
                book_serializer.save()

                request.session["mensagem"] = "Novo Livro Cadastrado com Sucesso!"
                return redirect("success")
            except ValidationError as e:
                request.session["mensagem"] = e.detail
                request.session["error_type"] = "Registro de Livro"
                return redirect("error")

    return render(
        request,
        "regist_book.html",
        {
            "user": get_user_from_email(request.user),
            "icon": get_user_from_email(request.user)["complete_name"][0],
        },
    )


@login_required
def inactive_book(request):
    if not request.user.is_authenticated:
        return redirect("/")

    if not request.user.is_superuser:
        return redirect("/home")

    books_queryset = Book.objects.filter(available_quantity__gt=0, is_active=True)

    book_serializer = BookSerializer(data=books_queryset, many=True)
    book_serializer.is_valid()

    active_books = book_serializer.data

    if request.method == "POST":
        book_id = request.POST.get("books_ids_list")

        book = Book.objects.get(id=book_id)
        book.is_active = False
        book.save()

        request.session["mensagem"] = "Livro Inativado com Sucesso!"
        return redirect("success")

    return render(
        request,
        "deactivate_book.html",
        {
            "user": get_user_from_email(request.user),
            "icon": get_user_from_email(request.user)["complete_name"][0],
            "active_books_list": active_books,
        },
    )


@login_required
def regist_loans(request):
    if not request.user.is_authenticated:
        return redirect("/")

    if not request.user.is_superuser:
        return redirect("/home")

    users = get_all_users()
    books = get_all_active_books()

    if request.method == "POST":
        user_id = request.POST.get("users_ids")
        book_id = request.POST.get("books_ids")
        aproved_date = request.POST.get("aproved_date")
        expected_devolution_date = request.POST.get("expected_devolution_date")
        loan_status = request.POST.get("status")

        formated_aproved_date = datetime.strptime(aproved_date, "%Y-%m-%d").strftime(
            "%Y-%m-%d"
        )
        formated_expected_devolution_date = datetime.strptime(
            expected_devolution_date, "%Y-%m-%d"
        ).strftime("%Y-%m-%d")

        validation_camps = validate_loan_regist_camps(
            user_id,
            book_id,
            formated_aproved_date,
            formated_expected_devolution_date,
            loan_status,
        )

        if not validation_camps["status"]:
            return render(
                request,
                "regist_loan.html",
                {
                    "user": get_user_from_email(request.user),
                    "icon": get_user_from_email(request.user)["complete_name"][0],
                    "users_list": users,
                    "books_list": books,
                    "saved_data": {
                        "user_data": user_id,
                        "book_data": book_id,
                        "aproved_date": aproved_date,
                        "expected_devolution_date": expected_devolution_date,
                        "status": loan_status,
                    },
                    "error": validation_camps["error"],
                },
            )
        else:
            try:
                loan_serializer = LoanSerializer(
                    data={
                        "user": user_id,
                        "book": book_id,
                        "aproved_date": formated_aproved_date,
                        "expected_devolution_date": formated_expected_devolution_date,
                        "status": loan_status,
                        "devolution_date": (
                            datetime.now().strftime("%Y-%m-%d")
                            if loan_status == "concluído"
                            else None
                        ),
                    }
                )
                loan_serializer.is_valid(raise_exception=True)
                loan_serializer.save()
                request.session["mensagem"] = "Emprestimo cadastrado com Sucesso!"
                return redirect("success")
            except ValidationError as e:
                request.session["mensagem"] = e.detail
                request.session["error_type"] = "Registro de Emprestimo"
                return redirect("error")

    return render(
        request,
        "regist_loan.html",
        {
            "user": get_user_from_email(request.user),
            "icon": get_user_from_email(request.user)["complete_name"][0],
            "users_list": users,
            "books_list": books,
        },
    )


@login_required
def regist_devolution(request):
    if not request.user.is_authenticated:
        return redirect("/")

    if not request.user.is_superuser:
        return redirect("/home")

    active_loans = get_oppening_loans()

    if request.method == "POST":
        loan_id = request.POST.get("loans_ids")
        loan_devolution_date = request.POST.get("devolution_date")
        loan_observation = request.POST.get("observation")

        print("observation", request.POST.get("observation"))

        camps_validation = devolution_validate_camps(
            loan_id=loan_id, devolution_date=loan_devolution_date
        )

        if not camps_validation["status"]:
            return render(
                request,
                "regist_devolution.html",
                {
                    "user": get_user_from_email(request.user),
                    "icon": get_user_from_email(request.user)["complete_name"][0],
                    "loans_list": active_loans,
                    "saved_data": {
                        "loan_id": loan_id,
                        "devolution_date": loan_devolution_date,
                        "observation": loan_observation.strip(),
                    },
                    "error": camps_validation["error"],
                },
            )
        else:
            try:
                loan = Loan.objects.get(id=loan_id)
                formated_devolution_date = datetime.strptime(
                    loan_devolution_date, "%Y-%m-%d"
                ).strftime("%Y-%m-%d")
                loan.devolution_date = formated_devolution_date
                loan.observation = loan_observation
                loan.status = "concluído"
                loan.save()
                request.session["mensagem"] = "Emprestimo devolvido com sucesso!"
                return redirect("success")
            except ValidationError as e:
                request.session["mensagem"] = e.detail
                request.session["error_type"] = "Registro de Devolução"
                return redirect("error")

    return render(
        request,
        "regist_devolution.html",
        {
            "user": get_user_from_email(request.user),
            "icon": get_user_from_email(request.user)["complete_name"][0],
            "loans_list": active_loans,
        },
    )


@login_required
def loans_relatory(request):
    if not request.user.is_authenticated:
        return redirect("/")

    if not request.user.is_superuser:
        return redirect("/home")

    return render(
        request,
        "regist_devolution.html",
        {
            "user": get_user_from_email(request.user),
            "icon": get_user_from_email(request.user)["complete_name"][0],
        },
    )


@login_required
def success(request):
    if not request.user.is_authenticated:
        return redirect("/")

    if not request.user.is_superuser:
        return redirect("/home")

    return render(
        request,
        "success.html",
        {
            "user": get_user_from_email(request.user),
            "icon": get_user_from_email(request.user)["complete_name"][0],
        },
    )


@login_required
def error(request):
    if not request.user.is_authenticated:
        return redirect("/")

    if not request.user.is_superuser:
        return redirect("/home")

    return render(
        request,
        "error.html",
        {
            "user": get_user_from_email(request.user),
            "icon": get_user_from_email(request.user)["complete_name"][0],
        },
    )


@login_required
def user_loans_relatory(request):
    if not request.user.is_authenticated:
        return redirect("/")

    user = User.objects.get(email=request.user.email)
    loans = Loan.objects.filter(user=user.id)

    formated_data = format_loans_to_tempalte(loans)

    if request.method == "POST":
        start_date = request.POST.get("initial_date")
        end_date = request.POST.get("final_date")

        formated_start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime(
            "%Y-%m-%d"
        )
        formated_end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y-%m-%d")

        filtered_loans = get_loans_by_period(
            formated_start_date, formated_end_date, user
        )

        return render(
            request,
            "user_loans_relatory.html",
            {
                "user": get_user_from_email(request.user),
                "icon": get_user_from_email(request.user)["complete_name"][0],
                "saved_data": {"initial_date": start_date, "final_date": end_date},
                "list": filtered_loans,
            },
        )

    return render(
        request,
        "user_loans_relatory.html",
        {
            "user": get_user_from_email(request.user),
            "icon": get_user_from_email(request.user)["complete_name"][0],
            "list": formated_data,
        },
    )


@login_required
def admin_loans_relatory(request):
    if not request.user.is_authenticated:
        return redirect("/")

    if not request.user.is_superuser:
        return redirect("/home")

    loans = Loan.objects.all()

    formated_loans = format_loans_to_tempalte(loans)

    if request.method == "POST":
        start_date = request.POST.get("initial_date")
        end_date = request.POST.get("final_date")

        formated_start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime(
            "%Y-%m-%d"
        )
        formated_end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y-%m-%d")

        filtered_loans = get_loans_by_period(formated_start_date, formated_end_date)

        return render(
            request,
            "admin_loans_relatory.html",
            {
                "user": get_user_from_email(request.user),
                "icon": get_user_from_email(request.user)["complete_name"][0],
                "saved_data": {"initial_date": start_date, "final_date": end_date},
                "list": filtered_loans,
            },
        )

    return render(
        request,
        "admin_loans_relatory.html",
        {
            "user": get_user_from_email(request.user),
            "icon": get_user_from_email(request.user)["complete_name"][0],
            "list": formated_loans,
        },
    )
