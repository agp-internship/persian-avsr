FROM python:3.8-slim
WORKDIR /code

RUN apt-get update \
    && apt-get install -y --no-install-recommends git wget\
    && apt-get purge -y --auto-remove
RUN git clone https://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@github.com/AmirMohamadBabaee/persian-avsr.git .
RUN cd ./data-collection/Babaei/ && pip install -r requirements.txt
RUN cd ./data-collection/Babaei \
    && bash init_workdir.sh
WORKDIR /code/data-collection/Babaei
CMD ["python", "main.py", '-rf', '--download', '480']