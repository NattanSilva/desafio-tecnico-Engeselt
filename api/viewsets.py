from datetime import date

from django.shortcuts import render
from rest_framework.views import Response, status
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Address, Book, Loan, User
from .permissions import (
    IsAdminOrReadOnly,
    IsAdminToCreateABook,
    IsAuthenticatedOrReadOnly,
)
from .serializers import (
    AddressSerializer,
    BookSerializer,
    LoanSerializer,
    UserSerializer,
)
from .utils import get_loan_by_id, validate_gt_loan_date


# Create your views here.
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrReadOnly]


class LoginViewset(ViewSet):
    serializer_class = TokenObtainPairSerializer

    def create(self, request, *args, **kwargs):
        view = TokenObtainPairView.as_view()

        return view(request._request, *args, **kwargs)


class AddressViewSet(ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrReadOnly]


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminToCreateABook]


class LoanViewSet(ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        book = Book.objects.get(id=request.data["book"])

        serializer = LoanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        print(serializer.data)

        expected_devolution_date = serializer.data["expected_devolution_date"]
        aproved_date = serializer.data["aproved_date"]
        devolution_date = serializer.data["devolution_date"]

        # Validação se o livro possui quantidade disponível ou esta ativo
        if book.available_quantity <= 0 or book.is_active == False:
            return Response(
                {
                    "error": "Livro Indisponivel no momento",
                    "detail": "livro indisponível ou inativo no momento",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validação se a data de devolução prevista é maior que a data atual(data de criação do emprestimo)
        if not validate_gt_loan_date(
            date.today().strftime("%Y-%m-%d"), expected_devolution_date
        ):
            return Response(
                {
                    "error": "Data de devolução prevista inválida",
                    "detail": "Data de devolução prevista deve ser maior que a data atual",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validação se a data de devolução prevista é diferente da data atual
        if expected_devolution_date == date.today().strftime("%Y-%m-%d"):
            return Response(
                {
                    "error": "Data de devolução prevista inválida",
                    "detail": "Data de devolução prevista deve ser maior que a data atual",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if aproved_date is not None:

            # Validação se a data de aprovação do emprestimo é igual a data de hoje
            if not validate_gt_loan_date(
                date.today().strftime("%Y-%m-%d"), aproved_date
            ) or aproved_date != date.today().strftime("%Y-%m-%d"):
                return Response(
                    {
                        "error": "Data de aprovação do emprestimo inválida",
                        "detail": "Data de aprovação do emprestimo deve ser igual a data atual",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if devolution_date is not None:
                # Validação se a data de devolução é maior que a data de aprovação do emprestimo
                if not validate_gt_loan_date(aproved_date, devolution_date):
                    return Response(
                        {
                            "error": "Data de devolução inválida",
                            "detail": "Data de devolução deve ser maior que a data de aprovação do emprestimo",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            if aproved_date is not None and devolution_date is None:
                request.data["status"] = "em aberto"

                # Atualização de quantidade disponível do livro
                book.available_quantity -= 1
                book.save()

            if aproved_date is not None and devolution_date is not None:
                request.data["status"] = "concluído"

                # Atualização de quantidade disponível do livro
                book.available_quantity += 1
                book.save()

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        loan_id = kwargs.get("pk")
        loan = get_loan_by_id(loan_id)

        if loan is None:
            return Response(
                {"error": "Emprestimo inexistente", "detail": "Emprestimo inexistente"},
                status=status.HTTP_404_NOT_FOUND,
            )

        print("loan - ", loan["book"])
        book = Book.objects.get(id=loan["book"])

        serializer = LoanSerializer(data=request.data)
        serializer.is_valid()

        expected_devolution_date = (
            serializer.data["expected_devolution_date"]
            if "expected_devolution_date" in serializer.data
            else None
        )
        aproved_date = (
            serializer.data["aproved_date"]
            if "aproved_date" in serializer.data
            else None
        )
        devolution_date = (
            serializer.data["devolution_date"]
            if "devolution_date" in serializer.data
            else None
        )
        loan_status = serializer.data["status"] if "status" in serializer.data else None

        # Validação se a data de devolução prevista é maior que a data atual(data de criação do emprestimo)
        if expected_devolution_date is not None and not validate_gt_loan_date(
            date.today().strftime("%Y-%m-%d"), expected_devolution_date
        ):
            return Response(
                {
                    "error": "Data de devolução prevista inválida",
                    "detail": "Data de devolução prevista deve ser maior que a data atual",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validação se a data de devolução prevista é diferente da data atual
        if (
            expected_devolution_date is not None
            and expected_devolution_date == date.today().strftime("%Y-%m-%d")
        ):
            return Response(
                {
                    "error": "Data de devolução prevista inválida",
                    "detail": "Data de devolução prevista deve ser maior que a data atual",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            loan_status is not None
            and loan_status == "em aberto"
            and loan["aproved_date"] is None
        ):
            serializer.data["aproved_date"] = date.today().strftime("%Y-%m-%d")

        if (
            loan_status is not None
            and loan_status == "concluído"
            and loan["aproved_date"] is not None
            and loan["status"] != "concluído"
        ):
            # Atualização de quantidade disponível do livro
            book.available_quantity += 1
            book.save()

            # Atualização da data de devolução do emprestimo
            request.data["devolution_date"] = date.today().strftime("%Y-%m-%d")
        elif (
            loan_status is not None
            and loan_status == "concluído"
            and loan["aproved_date"] is None
        ):
            return Response(
                {
                    "error": "Atualização de status invalida",
                    "detail": "Emprestimo do livro ainda não foi aprovado",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if aproved_date is not None and loan["aproved_date"] is None:

            # Validação se a data de aprovação do emprestimo é igual a data de hoje
            if not validate_gt_loan_date(
                date.today().strftime("%Y-%m-%d"), aproved_date
            ) or aproved_date != date.today().strftime("%Y-%m-%d"):
                return Response(
                    {
                        "error": "Data de aprovação do emprestimo inválida",
                        "detail": "Data de aprovação do emprestimo deve ser igual a data atual",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer.data["status"] = "em aberto"
            # Atualização de quantidade disponível do livro
            book.available_quantity -= 1
            book.save()
        elif aproved_date is not None and loan["aproved_date"] is not None:
            return Response(
                {
                    "error": "Data de aprovação inválida",
                    "detail": "Data de aprovação do emprestimo já preenchida",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if devolution_date is not None and loan["aproved_date"] is not None:
            print("entrou no if do devolution_date")
            # Validação se a data de devolução é maior que a data de aprovação do emprestimo
            if not validate_gt_loan_date(
                loan["aproved_date"], devolution_date
            ) or not validate_gt_loan_date(aproved_date, devolution_date):
                return Response(
                    {
                        "error": "Data de devolução inválida",
                        "detail": "Data de devolução deve ser maior que a data de aprovação do emprestimo",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if loan_status is None:
                serializer.data["status"] = "concluído"

                # Atualização de quantidade disponível do livro
                book.available_quantity += 1
                book.save()
        elif devolution_date is not None and loan["aproved_date"] is None:
            return Response(
                {
                    "error": "Data de devolução inválida",
                    "detail": "Emprestimo não pode ser concluído sem a data de aprovação do emprestimo",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        loan_id = kwargs.get("pk")
        loan = get_loan_by_id(loan_id)

        if loan is None:
            return Response(
                {"error": "Emprestimo inexistente", "detail": "Emprestimo inexistente"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        book = Book.objects.get(id=loan["book"])
        
        # Caso eu delete o emprestimo eu tenho o status diferente de concluído, logo a quantidade disponível do livro aumenta
        if loan["status"] != "concluído":
            
            book.available_quantity += 1
            book.save()

        return super().destroy(request, *args, **kwargs)
