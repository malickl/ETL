FROM python:3.11-slim

WORKDIR /app

# Copie du fichier requirements
COPY requirements.txt .

# Mise à jour de pip et installation forcée des dépendances
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copie du reste du projet
COPY . .

CMD ["python", "src/main.py"]