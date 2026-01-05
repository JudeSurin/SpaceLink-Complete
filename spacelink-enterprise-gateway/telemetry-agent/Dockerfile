FROM python:3.12-slim

WORKDIR /agent

# Install dependencies
RUN pip install --no-cache-dir requests pyyaml

# Copy agent code and config
COPY agent.py .
COPY config.yaml .

# Make agent executable
RUN chmod +x agent.py

# Run agent
CMD ["python", "agent.py"]
