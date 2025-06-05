FROM python:3.9

RUN apt-get update && apt-get install -y \
    g++ \
    build-essential \
    wget \
    curl \
    git \
    libpq-dev \
    libgdal-dev \
    gdal-bin \
    libspatialindex-dev \
    libgeos-dev \
    python3-dev \
    python3-pip \
    ssh \
    rsync \
    default-jdk \
    && apt-get clean

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

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

ENTRYPOINT ["bash", "-c", "source /etc/profile.d/java.sh && python filtrado.py"]
