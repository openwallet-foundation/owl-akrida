FROM ghcr.io/openwallet-foundation/acapy-agent:py3.12-1.2.2

USER root
ENV POETRY_HOME=/opt/poetry \
    VENV=/usr/src/app/.venv
ENV PATH="$POETRY_HOME/bin:$VENV/bin:$PATH"

#RUN curl -sSL https://install.python-poetry.org | python3 -
# Fixes installation failure
RUN pip3 install --no-cache-dir poetry
USER aries
RUN poetry config virtualenvs.create true; poetry config virtualenvs.in-project true

#RUN mkdir acapy_cache_redis && touch acapy_cache_redis/__init__.py
COPY --chown=aries:aries pyproject.toml poetry.lock ./

RUN poetry install --no-root 

# Make site packages location more accessible (for use with volumes)
#RUN ln -s $(poetry env info -p)/lib/python3.6/site-packages site-packages

#COPY --chown=aries:aries docker/default.yml .
COPY --chown=aries:aries afj_load_testing/ afj_load_testing/

#ENTRYPOINT ["/bin/bash", "-c", "aca-py \"$@\"", "--"]
ENTRYPOINT ["/bin/bash", "-c", "poetry run aca-py \"$@\"", "--"]
CMD ["start", "--arg-file", "default.yml"]
