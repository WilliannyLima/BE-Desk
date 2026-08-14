<p align="center">
  <img src="https://img.shields.io/badge/BE_Desk-Gestão_e_Reservas-007BFF?style=for-the-badge&logo=basketball" alt="BE-Desk Banner">
</p>

<h1 align="center">🏀 BE-Desk 📋</h1>

<p align="center">
  <strong>Organização e praticidade ao seu alcance.</strong><br>
  Sistema online de cadastro, reservas e solicitação de materiais esportivos para o Bloco E do IFRN.
</p>

---

## 📖 Sobre o Projeto

O **BE-Desk** nasceu para modernizar e digitalizar o processo de empréstimo e reserva de materiais esportivos e didáticos do Bloco E do IFRN. 

Combinamos a necessidade de um controle interno rigoroso com a facilidade de acesso para os alunos e servidores. O sistema substitui os antigos registros manuais por uma plataforma digital intuitiva, ágil e acessível para toda a comunidade acadêmica.

### 🚀 Funcionalidades Principais
- [x] **Reserva de Materiais:** Solicitação e agendamento de materiais esportivos em tempo real.
- [x] **Controle de Disponibilidade:** Visualização instantânea dos itens livres ou ocupados.
- [x] **Cadastro Geral:** Gerenciamento centralizado de usuários, alunos e servidores.
- [x] **Sistema de Notificações:** Alertas sobre prazos de devolução e status de reservas.
- [x] **Relatórios Administrativos:** Emissão de dados e estatísticas de uso para a gestão do bloco.

---

## 🛠 Tecnologias Utilizadas

As principais ferramentas usadas no desenvolvimento do sistema:

- [**Python / Django**](https://www.djangoproject.com/) - Core do sistema, lógica de negócio e painel administrativo.
- [**HTML5 / CSS3 / JavaScript**](https://developer.mozilla.org/pt-BR/) - Interface responsiva para dispositivos móveis e desktops.
- [**SQLite**](https://www.sqlite.org/index.html) - Banco de dados (ambiente de desenvolvimento).
- [**Docker / Nginx**](https://www.docker.com/) - Containerização e servidor para deploys robustos e seguros.

---

<h2 align="center">🚀 Como Executar o Projeto</h2>

<p align="center">
  Siga os passos abaixo para configurar e iniciar o <strong>BE-Desk</strong> em ambiente de desenvolvimento.
</p>

<br>

### 📦 1. Clone o repositório

```bash
git clone (https://github.com/WallisonAndre/BE-Desk.git)>
cd BE-Desk
````

### 🐍 2. Crie um ambiente virtual

```bash
python -m venv venv
```

### ▶️ 3. Ative o ambiente virtual

**Windows (PowerShell/CMD):**

```bash
.\venv\Scripts\activate
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

### 📥 4. Instale as dependências

Caso exista o arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

Ou instale manualmente:

```bash
pip install django requests
```

### 🗄️ 5. Configure o banco de dados

```bash
python manage.py makemigrations
python manage.py migrate
```

### ▶️ 6. Inicie o servidor

```bash
python manage.py runserver
```

### 🌐 7. Acesse o sistema

Abra o navegador e acesse:

```text
http://127.0.0.1:8000/
```


