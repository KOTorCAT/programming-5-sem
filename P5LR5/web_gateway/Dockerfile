FROM python:3.9-slim

WORKDIR /app

COPY web_gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY protobufs/glossary.proto /protobufs/
RUN python -m grpc_tools.protoc -I/protobufs --python_out=. --grpc_python_out=. /protobufs/glossary.proto

COPY web_gateway/ .

EXPOSE 5000
ENV FLASK_APP=app.py
CMD ["flask", "run", "--host=0.0.0.0"]