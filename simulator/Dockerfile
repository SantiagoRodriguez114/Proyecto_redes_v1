FROM python:3.11-slim
WORKDIR /sim
COPY sim.py /sim/
RUN pip install --no-cache-dir paho-mqtt
CMD ["python", "sim.py"]
