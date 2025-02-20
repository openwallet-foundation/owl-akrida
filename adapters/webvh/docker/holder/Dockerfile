FROM ghcr.io/openwallet-foundation/acapy-agent:py3.12-nightly

USER root

# install plugins as binaries
RUN pip install git+https://github.com/OpSecId/acapy-plugins@webvh-anoncreds#subdirectory=webvh

USER $user
COPY ./configs.yml configs.yml

CMD ["start", "--arg-file", "configs.yml"]