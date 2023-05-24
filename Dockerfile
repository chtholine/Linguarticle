FROM python:3.11.3

ENV PYTHONUNBUFFERED=1

ARG WORKDIR=/wd
ARG USER=user

WORKDIR ${WORKDIR}

RUN useradd --system ${USER} && \
    chown --recursive ${USER} ${WORKDIR}

RUN apt update && apt upgrade -y

COPY --chown=${USER} requirements.txt requirements.txt

RUN pip install --upgrade pip && \
    pip install --requirement requirements.txt


COPY --chown=${USER} --chmod=755 ./docker/app/start.sh /start.sh
COPY --chown=${USER} --chmod=755 ./docker/app/entrypoint.sh /entrypoint.sh

COPY --chown=${USER} ./apps apps
COPY --chown=${USER} ./core core
COPY --chown=${USER} ./scraper scraper
COPY --chown=${USER} ./Makefile Makefile
COPY --chown=${USER} ./manage.py manage.py


USER ${USER}

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

CMD ["/start.sh"]