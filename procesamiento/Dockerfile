FROM python:3.9


RUN apt-get update && apt-get install -y \
    g++ \
    build-essential \
    wget \
    curl \
    git \
    python3-dev \
    python3-pip \
    ssh \
    rsync \
    default-jdk \
    && apt-get clean
    

ENV PIG_VERSION=0.17.0
RUN wget https://downloads.apache.org/pig/pig-${PIG_VERSION}/pig-${PIG_VERSION}.tar.gz -P /tmp && \
    tar -xzf /tmp/pig-${PIG_VERSION}.tar.gz -C /opt && \
    mv /opt/pig-${PIG_VERSION} /opt/pig && \
    rm /tmp/pig-${PIG_VERSION}.tar.gz

ENV PIG_HOME=/opt/pig
ENV PATH=$PATH:$PIG_HOME/bin


RUN echo "export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which javac))))" >> /etc/profile.d/java.sh && \
    echo "export PATH=\$JAVA_HOME/bin:\$PATH" >> /etc/profile.d/java.sh && \
    chmod +x /etc/profile.d/java.sh

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY hadoop-3.2.1.tar.gz /tmp/
RUN tar -xzf /tmp/hadoop-3.2.1.tar.gz -C /opt/ && \
    mv /opt/hadoop-3.2.1 /opt/hadoop && \
    rm /tmp/hadoop-3.2.1.tar.gz

ENV HADOOP_HOME=/opt/hadoop
ENV HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin

COPY . /app

ENTRYPOINT ["bash", "-c", "source /etc/profile.d/java.sh && python procesamiento.py"]
