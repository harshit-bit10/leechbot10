# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set environment variables if needed (e.g., for API keys, tokens)
# ENV YOUR_ENV_VAR=value

# Command to run the bot
CMD ["python", "bot.pyc"]
