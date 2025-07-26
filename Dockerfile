FROM python:3.10-slim

WORKDIR /app

COPY process_pdfs.py .

RUN pip install PyMuPDF

CMD ["python", "process_pdfs.py"]

