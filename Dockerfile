FROM astral/uv:python3.13-bookworm-slim
WORKDIR /app
COPY pyproject.toml uv.lock .
RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*
RUN uv sync
COPY . .
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
ENTRYPOINT ["entrypoint.sh"]
CMD ["uv", "run", "gunicorn", "--workers", "3", "--bind", "0.0.0.0:8000", "conexiones.wsgi:application"]
