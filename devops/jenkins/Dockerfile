FROM jenkins/jenkins:lts-jdk11

USER root

# 安装必要的系统工具
RUN apt-get update && \
    apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg2 \
    software-properties-common \
    python3 \
    python3-pip \
    nodejs \
    npm

# 安装Docker
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - && \
    add-apt-repository \
    "deb [arch=amd64] https://download.docker.com/linux/debian \
    $(lsb_release -cs) \
    stable" && \
    apt-get update && \
    apt-get install -y docker-ce docker-ce-cli containerd.io

# 安装Python工具
RUN pip3 install --no-cache-dir \
    pylint \
    pytest \
    pytest-cov \
    pytest-html \
    pytest-xdist

# 安装Jenkins插件
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli -f /usr/share/jenkins/ref/plugins.txt

USER jenkins 