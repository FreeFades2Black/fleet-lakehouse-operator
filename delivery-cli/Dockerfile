# Multi-stage, rootless, distroless container image for Federal Delivery CLI
# Base image aligned with DoD Platform One / Chainguard hardened Python baseline

# Build stage
FROM cgr.dev/chainguard/python:latest-dev AS builder
WORKDIR /app

# Copy dependency specifications
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final hardened production runtime (Distroless / Non-root 65532)
FROM cgr.dev/chainguard/python:latest
WORKDIR /app

# Copy installed dependencies and application code
COPY --from=builder /home/nonroot/.local /home/nonroot/.local
COPY delivery_cli.py /app/delivery_cli.py

# Enforce non-root execution per DoD Iron Bank STIG requirements
USER 65532:65532
ENV PATH="/home/nonroot/.local/bin:$PATH"
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "/app/delivery_cli.py"]
CMD ["--help"]
