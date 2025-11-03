FROM python:3.11-slim

LABEL org.opencontainers.image.source="https://github.com/stbenjam/claudelint"
LABEL org.opencontainers.image.description="A configurable, rule-based linter for Claude Code plugins"
LABEL org.opencontainers.image.licenses="Apache-2.0"

# Set working directory
WORKDIR /app

# Copy package files
COPY pyproject.toml /app/pyproject.toml
COPY README.md /app/README.md
COPY src/ /app/src/

# Install the package
RUN pip install --no-cache-dir /app

# Set default working directory for linting
WORKDIR /workspace

# Run linter by default
ENTRYPOINT ["claudelint"]
CMD []
