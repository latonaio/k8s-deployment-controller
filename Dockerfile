FROM latonaio/l4t:latest

# Definition of a Device & Service
ENV POSITION=Runtime \
    SERVICE=k8s-deployment-controller\
    AION_HOME=/var/lib/aion

# Setup Directoties
RUN mkdir -p \
    $POSITION/$SERVICE
WORKDIR ${AION_HOME}/$POSITION/$SERVICE/

RUN rm -rf /usr/local/lib/python3.6/dist-packages/protobuf*

ADD requirements.txt .
RUN pip3 install -r requirements.txt

ENV PYTHONPATH ${AION_HOME}/$POSITION/$SERVICE
ENV REGISTRY_USER aion

ADD src/ .

CMD ["python3", "-u", "main.py"]