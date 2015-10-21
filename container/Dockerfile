FROM ubuntu

RUN apt-get update
RUN apt-get install -y git-core python-pip
RUN pip install rq
RUN git clone git://github.com/jhallard/Praxyk
RUN cd Praxyk/pod && ./praxyk-build-pod.sh

EXPOSE 6379

CMD rqworker redis://fileserver.local:6379/0
