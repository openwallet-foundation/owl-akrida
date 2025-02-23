FROM ghcr.io/openwallet-foundation/acapy-agent:py3.12-nightly

USER root

# install plugins as binaries
RUN pip install git+https://github.com/OpSecId/acapy-plugins@webvh-anoncreds#subdirectory=webvh

USER $user
COPY ./config.yml config.yml

CMD ["start", "--arg-file", "config.yml"]