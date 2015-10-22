FROM ubuntu

RUN apt-get update
RUN apt-get install -y git-core python-pip
RUN pip install rq
RUN git clone git://github.com/jhallard/Praxyk -b container
RUN cd Praxyk/pod && ./praxyk-build-pod.sh
RUN cp -r Praxyk/container/api /

EXPOSE 6379
CMD cd /api && rqworker -u redis://192.168.1.126:6379/0
