FROM python:3.8

WORKDIR /home/myfirstapi/

RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
COPY . .

RUN pip install -r requirements.txt -q -i https://pypi.tuna.tsinghua.edu.cn/simple && \
rm -rf /var/cache/apk/*

expose 2222
CMD ["python3", "app.py"]