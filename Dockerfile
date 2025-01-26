FROM python:3.12-bullseye

RUN pip install poetry
RUN useradd tweyen -u 1000 && mkdir /home/tweyen && chown tweyen:tweyen /home/tweyen
COPY . /home/tweyen
WORKDIR /home/tweyen
RUN poetry build && pip install --find-links dist/ tweyen
RUN chown tweyen:tweyen -R .

USER tweyen

ENTRYPOINT ["bot"]
