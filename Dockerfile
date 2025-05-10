FROM archlinux:latest

WORKDIR /app

# Install system dependencies
RUN pacman -Syu --noconfirm --needed \
    base-devel \
    gcc \
    libffi \
    postgresql-libs \
    supervisor \
    python python-pip \
    git \
 && pacman -Scc --noconfirm

# Create a virtual environment
RUN python -m venv /app/ENV

# Install Python requirements
COPY requirements.txt .
RUN /app/ENV/bin/pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Make start script executable
RUN chmod +x start.sh

# Use a shell form to start both FastAPI apps and handle signals
ENTRYPOINT ["bash", "./start.sh"]
