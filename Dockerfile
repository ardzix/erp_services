#Base Image
FROM python:3.10

ENV PYTHONUNBUFFERED=1

#Install Package
RUN apt update && apt install -y \
    build-essential \
    binutils \
    libproj-dev \
    python3-gdal \
    python3-gdl \
    gdal-bin \
    net-tools 

# Create Folder
#RUN mkdir -p /api

#Set Workdir & Copy App
WORKDIR /app
COPY . .

#Install Python Package with requirements file
RUN pip install --no-cache-dir -r requirements.txt
#RUN pip install --no-cache-dir -r requirements-bahana.txt

#RUN chmod -R +x ./deploy/local
# migrate migration files
# RUN ./manage.py migrate

#Expose Port
# api
EXPOSE 8000

# flower
#EXPOSE 4444

# start server
#CMD ["gunicorn", "-c", "gunicorn_config.py", "project.wsgi", "--log-config", "gunicorn_logging.config"]
#CMD ["./deploy/local/run_api.sh"]
#RUN cp project/production_settings.py project/local_settings.py 

#RUN python3 manage.py makemigrations
#RUN python3 manage.py migrate

RUN mkdir -p static/upload
RUN echo yes | python3 manage.py collectstatic
CMD ["python3","manage.py","runserver","0.0.0.0:8000"]

