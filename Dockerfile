# --- STAGE 1: Define the Base ---
# Use an official, lightweight Linux image that matches your local Python 3.13.
FROM python:3.13-slim

# --- STAGE 2: Set up the Workspace ---
# Set the working directory inside the container to a folder named /app.
# All subsequent commands will run from here.
WORKDIR /app

# --- STAGE 3: Install System Dependencies ---
# Some of Python packages need basic Linux tools to be installed first.
RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev libxslt-dev \
    libglib2.0-0 libnss3 libnspr4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 \
    && rm -rf /var/lib/apt/lists/*

# --- STAGE 4: Install Python Packages ---
# Copy ONLY the requirements file into the container.
# We do this first so Docker can cache this step. If requirements.txt doesn't change, this layer won't have to be rebuilt, saving time.
COPY requirements.txt .

# Now, run pip install using the requirements file.
RUN pip install --no-cache-dir -r requirements.txt

# The 'playwright' library needs a special command to download its browsers.
RUN playwright install --with-deps

# --- STAGE 5: Copy Your Application Code ---
# Now that all dependencies are installed, copy the rest of the project files (main_server.py, etc.) into the container.
COPY . .

# --- STAGE 6: Configure and Run ---
# Tell Docker that your application will be listening for network traffic on port 8000.
EXPOSE 8000

# Set the PYTHONUNBUFFERED environment variable to force logs to appear in real-time
ENV PYTHONUNBUFFERED=1

# This is the final command to the application.
# It's the container's version of running "python main_server.py".
# It tells uvicorn to run the 'app' object from the 'main_server.py' file.
CMD ["uvicorn", "main_server:app", "--host", "0.0.0.0", "--port", "8000"]