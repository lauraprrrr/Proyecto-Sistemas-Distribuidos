FROM python:3.9

RUN apt-get update && \
    apt-get install -y wget ssh rsync default-jdk && \
    apt-get clean

# Detecta JAVA_HOME dinámicamente
RUN echo "export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which javac))))" >> /etc/profile.d/java.sh && \
    echo "export PATH=\$JAVA_HOME/bin:\$PATH" >> /etc/profile.d/java.sh

# Instala Hadoop
COPY hadoop-3.2.1.tar.gz /tmp/
RUN tar -xzf /tmp/hadoop-3.2.1.tar.gz -C /opt/ && \
    mv /opt/hadoop-3.2.1 /opt/hadoop && \
    rm /tmp/hadoop-3.2.1.tar.gz


ENV HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin

COPY . /app
WORKDIR /app

RUN chmod +x /etc/profile.d/java.sh
ENTRYPOINT ["bash", "-c", "source /etc/profile.d/java.sh && python filtrado.py"]
