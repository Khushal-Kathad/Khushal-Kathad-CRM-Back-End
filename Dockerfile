FROM python:3.12.8


WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    apt-transport-https \
    unixodbc-dev \
&& curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
&& curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
&& apt-get update \
&& ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/*
 
# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


 
# Copy the FastAPI application code
COPY . .
 
# Expose the default FastAPI port
EXPOSE 8080
 
# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]





