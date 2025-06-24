FROM ghcr.io/openwallet-foundation/acapy-agent:py3.12-1.3.0

# RUN pip install 'git+https://github.com/Indicio-tech/aries-acapy-cache-redis.git@154e2d01566bcea67b503e862a1843302096ed29'
#RUN pip install 'git+https://github.com/AlexanderShenshin/aries-acapy-cache-redis.git@04ba26650241eaab1d6b92e6970c5cefbb66051d'
RUN pip install 'git+https://github.com/KimEbert42/aries-acapy-cache-redis.git@f737d21712378ac53f66b82ee5f10c1264f5d5f9'

USER $user

#ENTRYPOINT ["/bin/bash", "-c", "aca-py \"$@\"", "--"]
ENTRYPOINT ["/bin/bash", "-c", "aca-py \"$@\"", "--"]
CMD ["start", "--arg-file", "default.yml"]
