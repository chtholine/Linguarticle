FROM ubuntu:latest
LABEL authors="chtholine"

ENTRYPOINT ["top", "-b"]