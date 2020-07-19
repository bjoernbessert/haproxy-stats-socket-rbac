ARG UBUNTU_DOCKER_IMAGE
FROM $UBUNTU_DOCKER_IMAGE

ARG HAPROXY_MAIN_VERSION

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -yq tzdata
RUN echo Europe/Berlin >/etc/timezone && \
    ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

RUN apt-get update && apt-get install -yq software-properties-common

RUN add-apt-repository -y ppa:vbernat/haproxy-$HAPROXY_MAIN_VERSION && apt-get update && \
    apt-get install -yq haproxy=$HAPROXY_MAIN_VERSION.\* 

RUN apt-get update && apt-get install -yq python3-yaml

RUN apt-get update && apt-get install -yq supervisor
RUN mkdir -p /var/log/supervisor
COPY files/supervisord.conf /etc/supervisor/supervisord.conf

RUN apt-get update && apt-get install -yq netcat socat iputils-ping curl wget less vim psmisc net-tools

RUN mkdir /etc/haproxy/certs
COPY files/fallback.example.local.pem /etc/haproxy/certs/

RUN mkdir /opt/haproxy-stats-socket-rbac

RUN rm -f /etc/haproxy/haproxy.cfg
COPY files/haproxy.cfg /etc/haproxy/haproxy.cfg

# For local testing
COPY files/ca.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates

# Info
RUN haproxy -vv

RUN echo "export TERM=xterm" >> /etc/bash.bashrc

RUN apt-get autoremove -y
RUN apt-get clean
RUN rm -rf /var/lib/{apt,dpkg,cache,log}/

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
