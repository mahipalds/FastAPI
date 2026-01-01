#base image
FROM python:3.11-slim
# Seting working directory inside container
WORKDIR /app 
# Copy only requirements first to leverage Docker cache
COPY requirements.txt .
#install dependencies 
RUN pip install --no-cache-dir -r requirements.txt 

#copy the rest of the project files
COPY . .

#Expose port for FastAPI
EXPOSE 8000

#command to run FastAPI using uvicorn 
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]