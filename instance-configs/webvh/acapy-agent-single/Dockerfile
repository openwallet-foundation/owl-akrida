FROM ghcr.io/openwallet-foundation/acapy-agent:py3.12-1.3.0

USER root

# install plugins as binaries
RUN pip install git+https://github.com/openwallet-foundation/acapy-plugins@1.3.0#subdirectory=webvh

USER $user
COPY ./config.yml config.yml

CMD ["start", "--arg-file", "config.yml"]
