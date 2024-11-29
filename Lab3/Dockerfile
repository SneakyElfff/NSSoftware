FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 python3-pip openmpi-bin openmpi-common openmpi-doc openssh-client openssh-server libopenmpi-dev

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

RUN mkdir /var/run/sshd && \
    echo 'root:root' | chpasswd && \
    ssh-keygen -A && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config && \
    echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config

RUN mkdir -p /root/.ssh && \
    chmod 700 /root/.ssh

WORKDIR /app
COPY . /app

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]