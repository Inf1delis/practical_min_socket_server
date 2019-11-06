FROM python:3

RUN pip3 install redis

COPY echo-server.py /

EXPOSE 65432

ENTRYPOINT ["python", "echo-server.py"]

