FROM mcr.microsoft.com/devcontainers/python:3.12

# Install Node.js and Claude Code CLI
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - \
    && sudo apt-get install -y nodejs \
    && npm install -g @anthropic-ai/claude-code

# Install Python dependencies
COPY requirements.txt requirements-dev.txt /tmp/
RUN pip install --upgrade pip \
    && pip install -r /tmp/requirements.txt -r /tmp/requirements-dev.txt

# Install Playwright browsers to a stable, version-agnostic location
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers
RUN playwright install chromium && playwright install-deps chromium
