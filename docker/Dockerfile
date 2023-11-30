ARG PYTHON_VERSION=3.7
FROM sregistry.mts.ru/bigdata/platform/docker-images/python:${PYTHON_VERSION}-slim as base
ENV REQUESTS_CA_BUNDLE=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem
ENV CURL_CA_BUNDLE=$REQUESTS_CA_BUNDLE \
    SSL_CERT_FILE=$REQUESTS_CA_BUNDLE

RUN microdnf install -y libnghttp2-1.33.0-3.el8_2.1 libpq-devel make git gzip && microdnf clean all
ENV PROJECT_USER=horizon-hwm-store
ENV PROJECT_USER_HOME=/home/$PROJECT_USER
RUN useradd $PROJECT_USER -d $PROJECT_USER_HOME
ENV PATH="$PROJECT_USER_HOME/.local/bin:$PATH"

WORKDIR /app
USER $PROJECT_USER

RUN pip install -U setuptools wheel
COPY --chown=$PROJECT_USER:$PROJECT_USER ./requirements.txt ./requirements-test.txt ./
RUN  pip install  -r ./requirements.txt  -r ./requirements-test.txt


FROM base as ci

COPY --chown=$PROJECT_USER:$PROJECT_USER ./requirements-dev.txt ./requirements-docs.txt /app/
RUN pip install -r ./requirements-docs.txt -r ./requirements-dev.txt
