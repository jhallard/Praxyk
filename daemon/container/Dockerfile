FROM ubuntu
RUN apt-get update
RUN apt-get install -y git-core python-pip
RUN pip install rq
RUN git clone --recursive git://github.com/Praxyk/Praxyk -b master
RUN cd Praxyk/pod && ./build.sh
RUN cp -r Praxyk/api /
RUN mkdir -p /drive1/img_store
ADD config.py /config.py
EXPOSE 6379
CMD cd / && rqworker -c config
