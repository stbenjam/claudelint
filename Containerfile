FROM python:3.11-slim

LABEL org.opencontainers.image.source="https://github.com/stbenjam/claudelint"
LABEL org.opencontainers.image.description="A configurable, rule-based linter for Claude Code plugins"
LABEL org.opencontainers.image.licenses="Apache-2.0"

# Set working directory
WORKDIR /app

# Copy application files
COPY src/ /app/src/
COPY rules/ /app/rules/
COPY claudelint /app/claudelint
COPY pyproject.toml /app/pyproject.toml
COPY README.md /app/README.md

# Install dependencies
RUN pip install --no-cache-dir PyYAML>=6.0 && \
    chmod +x /app/claudelint

# Add app to PATH
ENV PATH="/app:${PATH}"
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Set default working directory for linting
WORKDIR /workspace

# Run linter by default
ENTRYPOINT ["claudelint"]
CMD []

