FROM harbor.swokiz.dev/hub-proxy/library/python:3.12-slim

COPY --chown=1000:1000 requirements.txt /app/requirements.txt
COPY --chown=1000:1000 app.py /app/app.py
COPY --chown=1000:1000 receipt_service.py /app/receipt_service.py
COPY --chown=1000:1000 .streamlit /app/.streamlit
COPY --chown=1000:1000 res /app/res

WORKDIR /app

WORKDIR /app
ENV PYTHONPATH=/app
ENV STREAMLIT_CONFIG_DIR=/app/.streamlit

RUN useradd -m -u 1000 app \
 && chown -R 1000:1000 /app \
 && python3 -m pip install -r /app/requirements.txt

ENTRYPOINT ["python3", "-m", "streamlit", "run", "--server.address", "0.0.0.0", "app.py"]

EXPOSE 8501/tcp
