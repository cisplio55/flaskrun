FROM python:3.10
# WORKDIR .
# COPY output.csv .
# COPY swagger_yaml_to_excell.py .
# COPY openapi_modified.yml .
# COPY requirements.txt .
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
# CMD [ "flask", "run" ]
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]