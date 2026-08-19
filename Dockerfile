# syntax=docker/dockerfile:1

# =========================================================
# Stage 1: Builder
# Installs Python dependencies into an isolated virtual env.
# =========================================================
FROM python:3.14-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

# Create a virtual environment whose contents can be copied
# into the final runtime stage.
RUN python -m venv /opt/venv

# Make "python", "pip", and installed commands use the venv.
ENV PATH="/opt/venv/bin:$PATH"

# Copy dependency list first to preserve Docker layer caching.
COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt


# =========================================================
# Stage 2: Runtime
# Contains only Python, dependencies, and application code.
# =========================================================
FROM python:3.14-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    HOME=/home/allsafe

# Create an unprivileged system user.
RUN groupadd --system allsafe \
    && useradd \
        --system \
        --gid allsafe \
        --create-home \
        --home-dir /home/allsafe \
        allsafe

WORKDIR /allsafe

# Copy installed dependencies from the builder stage.
COPY --from=builder /opt/venv /opt/venv

# Copy only the application code needed at runtime.
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini

# All following runtime commands execute as this user.
USER allsafe

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]