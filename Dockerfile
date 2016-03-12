FROM python:2.7-alpine

MAINTAINER Leon de Jager <ldejager@coretanium.net>

RUN mkdir -p /opt/scripts/VMSuperHub

WORKDIR /opt/scripts/VMSuperHub/

COPY requirements.txt /opt/scripts/VMSuperHub/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /opt/scripts/VMSuperHub/

RUN /usr/local/bin/echo_supervisord_conf > /etc/supervisord.conf \
 && mkdir -p /etc/supervisor.d/ \
 && mv vmsuperhub.conf /etc/supervisor.d/vmsuperhub.conf \
 && sed -ie 's|;\[include\]|\[include\]|g;s|;files = relative/directory/\*.ini|files = /etc/supervisor.d/\*.conf|g' /etc/supervisord.conf

RUN ln -sf /dev/stdout /opt/scripts/VMSuperHub/vm_supervisor.out.log
RUN ln -sf /dev/stderr /opt/scripts/VMSuperHub/vm_supervisor.err.log

CMD ["supervisord", "-c", "/etc/supervisord.conf"]
