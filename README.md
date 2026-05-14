BE-Desk 🏀📚

Sistema online de cadastro, reservas e solicitação de materiais esportivos para o Bloco E do IFRN-SPP.

📖 Sobre o Projeto

O BE-Desk é um sistema desenvolvido para modernizar o processo de empréstimo e reserva de materiais esportivos do Bloco E do IFRN Campus São Paulo do Potengi.

Atualmente, o controle é realizado de forma presencial, e o projeto busca substituir esse modelo por uma solução digital, prática e acessível para toda a comunidade acadêmica.

🚀 Funcionalidades
📌 Cadastro de usuários
🏀 Reserva de materiais esportivos
📅 Controle de disponibilidade
🔔 Sistema de notificações
📊 Relatórios
🔐 Sistema de autenticação
🌐 Interface web responsiva
🛠️ Tecnologias Utilizadas
Python
Django
HTML5
CSS3
JavaScript
SQLite
Docker
Nginx
📂 Estrutura do Projeto
BE-DESK/
│
├── bedesk/
├── config/
├── core/
├── integracao_suap/
├── materiais/
├── nginx/
├── notificacoes/
├── relatorios/
├── reservas/
├── static/
├── templates/
├── usuarios/
│
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── requirements.txt
└── README.md
⚙️ Como Executar o Projeto
📌 Pré-requisitos

Antes de começar, você precisa ter instalado:

Python 3.x
Git
🔧 Instalação
1. Clone o repositório
git clone https://github.com/SEU-USUARIO/be-desk.git
2. Entre na pasta do projeto
cd be-desk
3. Crie um ambiente virtual
python -m venv venv
4. Ative o ambiente virtual
Windows
venv\Scripts\activate
Linux/MacOS
source venv/bin/activate
5. Instale as dependências
pip install -r requirements.txt
6. Execute as migrações
python manage.py migrate
7. Inicie o servidor
python manage.py runserver
🌐 Acesso ao Sistema

Após iniciar o servidor, acesse:

http://127.0.0.1:8000/
🐳 Executando com Docker
Iniciar containers
docker-compose up --build
Encerrar containers
docker-compose down
👨‍💻 Equipe
Igor Murilo
Wallison Andre
🎯 Objetivo

O principal objetivo do projeto é facilitar o acesso aos materiais esportivos do Bloco E, promovendo maior organização, transparência e praticidade para toda a comunidade acadêmica.

🏫 Instituição

Projeto Integrador — Curso Técnico em Informática para Internet
Instituto Federal do Rio Grande do Norte

📅 Ano

2025

📄 Licença

Este projeto possui fins acadêmicos e educacionais.
