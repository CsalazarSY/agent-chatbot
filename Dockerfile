# Dockerfile

# Empezamos desde nuestra imagen base que ya tiene todo instalado.
FROM syqaaichatbotregistry.azurecr.io/autogen-chatbot-base:1.0

# Establecemos el directorio de trabajo.
WORKDIR /app

# Copiamos TODO nuestro código fuente de la aplicación.
COPY . .

# Exponemos el puerto y definimos el comando de inicio.
EXPOSE 8000
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "main_server:app", "--host", "0.0.0.0", "--port", "8000"]