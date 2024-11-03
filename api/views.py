from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from rest_framework.serializers import ValidationError

from .models import User
from .serializers import AddressSerializer, UserSerializer, BookSerializer
from .utils import (
    get_user_from_email,
    validate_address_camps,
    validate_book_camps,
    validate_email_exists,
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

    print(request.user)

    return render(
        request,
        "home.html",
        {
            "user": get_user_from_email(request.user),
            "icon": get_user_from_email(request.user)["complete_name"][0],
            "items": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
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

            print(address_validation)
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

        print(book_camps_validation)

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

    return render(
        request,
        "deactivate_book.html",
        {
            "user": get_user_from_email(request.user),
            "icon": get_user_from_email(request.user)["complete_name"][0],
        },
    )


@login_required
def gerency_loans(request):
    if not request.user.is_authenticated:
        return redirect("/")

    if not request.user.is_superuser:
        return redirect("/home")

    return render(
        request,
        "gerency_loans.html",
        {
            "user": get_user_from_email(request.user),
            "icon": get_user_from_email(request.user)["complete_name"][0],
        },
    )


@login_required
def regist_devolution(request):
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
