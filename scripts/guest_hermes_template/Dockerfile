FROM nikolaik/python-nodejs:python3.11-nodejs20

# Prevent interactive prompts during apt install
ENV DEBIAN_FRONTEND=noninteractive

# Install essential system dependencies (needed for compiling pyswisseph)
RUN apt-get update && apt-get install -y \
    build-essential \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install Hermes Agent and all Human Design MCP + Mock MCP dependencies
RUN pip install --no-cache-dir \
    "hermes-agent[web,pty]" \
    mcp \
    pyyaml \
    pyswisseph \
    pydantic \
    numpy \
    timezonefinder \
    pytz \
    requests \
    pillow \
    matplotlib \
    ddgs \
    "anthropic>=0.39.0"

# Initialize the workspace and config folder structure under non-root user home
RUN mkdir -p /home/pn/.hermes /workspace && \
    chown -R pn:pn /home/pn /workspace

# Set work directory and run container as the non-root user pn (UID 1000)
WORKDIR /workspace
USER pn

# Entrypoint is hermes agent CLI
ENTRYPOINT ["hermes"]
CMD ["gateway", "run"]
