# Hugging Face Spaces — Panel Smart Home Dashboard
FROM python:3.10-slim

# HF Spaces runs containers as a non-root user (UID 1000).
# Create the user early so file ownership is correct.
RUN useradd -m -u 1000 user
USER user

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

WORKDIR /home/user/app

# Install dependencies first (layer-cached unless requirements.txt changes)
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=user . .

# Port 7860 is the only port HF Spaces exposes externally
EXPOSE 7860

# Use `panel serve` directly — this handles the Tornado event loop correctly,
# which is important for periodic callbacks and websocket streaming.
# --allow-websocket-origin "*" is required behind HF's reverse proxy.
CMD ["panel", "serve", "app.py", \
     "--address", "0.0.0.0", \
     "--port", "7860", \
     "--allow-websocket-origin", "*", \
     "--num-procs", "1"]