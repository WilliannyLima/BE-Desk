FROM python:3.12-slim

# Evita arquivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia TODO o projeto
COPY . .

# Coleta arquivos estáticos (se usar)
RUN python manage.py collectstatic --noinput || true

# Porta do Django
EXPOSE 8000

# Inicia o servidor
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
