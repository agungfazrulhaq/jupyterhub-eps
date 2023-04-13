ARG JUPYTERHUB_VERSION=3
FROM jupyterhub/jupyterhub:$JUPYTERHUB_VERSION
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-cache -r /tmp/requirements.txt
RUN apt-get update
RUN apt-get install -y npm nodejs python3 python3-pip git nano
RUN pip install jupyterhub jupyterlab notebook

COPY jupyterhub_config.py /srv/jupyterhub/jupyterhub_config.py
