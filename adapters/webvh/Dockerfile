FROM python:3.12

WORKDIR /flask

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY pyproject.toml ./

RUN pip install poetry
RUN poetry install

COPY models ./models
COPY interface ./interface
COPY locustfiles ./locustfiles
COPY controllers ./controllers
COPY web_ui.py settings.py ./

CMD [ "python", "web_ui.py" ]