FROM python
COPY /app ~/app
RUN pip install -r ~/app/requirements.txt

ENTRYPOINT ["python ~/app/service.py"]
