FROM k8sdev.mbbank.com.vn/common/python:3.8-il

ARG NEXUS_USER
ARG NEXUS_PASSWORD
ARG NEXUS_PYTHON_INDEX_URL
ARG NEXUS_PYTHON_TRUSTED_HOST

#Set up web app
WORKDIR /apartment-price-prediction
COPY ./requirements.txt /apartment-price-prediction/requirements.txt
RUN pip3 install -r /apartment-price-prediction/requirements.txt \
    -i http://${NEXUS_USER}:${NEXUS_PASSWORD}@${NEXUS_PYTHON_INDEX_URL} \
    --trusted-host ${NEXUS_PYTHON_TRUSTED_HOST}
COPY ./app /apartment-price-prediction/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "11108"]

EXPOSE 11108
