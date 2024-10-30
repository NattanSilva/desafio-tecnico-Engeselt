# Desafio Sistema de Controle de Biblioteca para a Genius Lab

<p>O Sistema de Controle de Biblioteca para a Genius Lab
representa uma inovação significativa no gerenciamento de
bibliotecas educacionais. Com uma interface amigável e
funcionalidades robustas, a plataforma digitaliza e simplifica
processos que tradicionalmente consomem tempo e recursos.
Administradores têm à disposição ferramentas avançadas para
catalogar novos livros, acompanhar o status dos empréstimos e
gerar relatórios que oferecem insights sobre a circulação dos
materiais. Isso não só melhora a eficiência operacional, mas
também permite decisões informadas para a expansão do
acervo. Por outro lado, os usuários desfrutam de uma
experiência otimizada, com acesso rápido a informações sobre
disponibilidade de livros e um histórico de empréstimos que
facilita a gestão pessoal de suas leituras. Essa solução não
apenas melhora o acesso aos recursos educacionais, mas
também promove um ambiente de aprendizagem mais
organizado e eficiente.</p>

### Dependências:

1. <a href="https://python.org.br/instalacao-windows/" target="_blank">Python3</a>
2. <a href="https://www.postgresql.org/download/" target="_blank">PostgreSQL</a>

### 1 - Crie seu ambiente virtual:

```shell
python -m venv venv
```

### 2 - Ative seu ambiente virtal:

```shell
# linux:
source venv/bin/activate

# windows (powershell):
.\venv\Scripts\activate

# windows (git bash):
source venv/Scripts/activate
```

### 3 - Instale as dependências do projeto:

```shell
pip install -r requirements.txt
```

### 4 - Crie uma nova Database local:

<p>Para executar o projeto localmente crie um banco de dados separado apenas para esta aplicação.</p>

```shell
# Acesse a shell do postgres no seu terminal com seu usuario e senha:
psql -U seu_usuario
# Crie uma nova Database com o comando:
CREATE DATABASE nome_do_seu_novo_banco_de_dados;
# Verifique se o Database foi criada corretamente:
\l
# Caso sua nova Database apareça na listagem de Databases tudo ocorreu com sucesso!
# Para sair da shell do postgres basta digitar o comando abaixo e pressionar enter:
\quit
```

### 5 - Configure sua conexão com o banco de dados:

<p>Para esta etapa copie o arquivo <code>.env.template</code> e mude o nome da cópia para <code>.env</code> e preencha os campos com as informações de acordo com as instruções a seguir.</p>

```shell
  # Python secret key
  SECRET_KEY="Your secret key"

  # Database configurations
  DB_ENGINE="django.db.backends.potgresql"
  DB_NAME="Name of your database"
  DB_USER="Your postgres username"
  DB_PASSWORD="Your postgres username"
  DB_HOST="Your localhost or your iddress IP"
  DB_PORT="Your postgres port(default 5432)"
```

### 6 - Gere as migrações:

```shell
python manage.py makemigrations
```

### 7 - Execute as migrações:

```shell
python manage.py migrate
```

### 8 - Inicie o servidor:

```shell
python manage.py runserver
```
