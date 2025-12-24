FROM python:3.9-slim

WORKDIR /app

COPY glossary_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY protobufs/glossary.proto /protobufs/
RUN python -m grpc_tools.protoc -I/protobufs --python_out=. --grpc_python_out=. /protobufs/glossary.proto

COPY glossary_service/ .

EXPOSE 50051
CMD ["python", "server.py"]