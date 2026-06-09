# We use the official Python 3.12 image as our starting point
FROM python:3.12-slim

# We set the working directory inside the container to /app
WORKDIR /app

# We copy our requirements file first to take advantage of Docker caching
COPY requirements.txt .

# We install all the packages we need
RUN pip install --no-cache-dir -r requirements.txt

# Now we copy the rest of our project files into the container
COPY . .

# We tell Docker that our app will run on port 8000
EXPOSE 8000

# Finally, this is the command that starts our FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
