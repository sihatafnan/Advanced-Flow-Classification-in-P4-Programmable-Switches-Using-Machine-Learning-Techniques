FROM opennetworking/mn-stratum:latest

RUN apt-get update && apt-get install -y \
    python-pip xterm xorg openbox
RUN pip install scapy


COPY ./topo/10.0.1.1.txt .
COPY ./topo/10.0.1.2.txt .
COPY ./topo/10.0.2.1.txt .
COPY ./topo/10.0.2.2.txt .
COPY ./topo/10.0.3.1.txt .
COPY ./topo/10.0.3.2.txt .
COPY ./topo/10.0.4.1.txt .
COPY ./topo/10.0.4.2.txt .
COPY ./topo/send-traffic.py .
COPY ./topo/receive-traffic.py .