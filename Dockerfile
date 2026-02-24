FROM harbor.swokiz.dev/hub-proxy/library/python:3.12-slim

COPY --chown=1000:1000 requirements.txt app.py receipt_service.py /app

WORKDIR /app

RUN python3 -m pip install -r requirements.txt

ENTRYPOINT ["python3", "-m", "streamlit", "run", "--server.address", "0.0.0.0", "app.py"]

EXPOSE 8501/tcp
