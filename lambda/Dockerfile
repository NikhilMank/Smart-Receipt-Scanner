FROM public.ecr.aws/lambda/python:3.12

# Install build dependencies and compile tesseract
RUN microdnf update -y && \
    microdnf install -y gcc gcc-c++ make cmake wget tar gzip \
    libjpeg-devel libpng-devel libtiff-devel zlib-devel \
    autoconf automake libtool pkgconfig poppler-utils && \
    microdnf clean all

# Install Leptonica
RUN cd /tmp && \
    wget http://www.leptonica.org/source/leptonica-1.82.0.tar.gz && \
    tar -xzf leptonica-1.82.0.tar.gz && \
    cd leptonica-1.82.0 && \
    ./configure --prefix=/usr/local && \
    make && make install

# Install Tesseract
RUN cd /tmp && \
    wget https://github.com/tesseract-ocr/tesseract/archive/5.3.0.tar.gz && \
    tar -xzf 5.3.0.tar.gz && \
    cd tesseract-5.3.0 && \
    ./autogen.sh && \
    PKG_CONFIG_PATH=/usr/local/lib/pkgconfig ./configure --prefix=/usr/local && \
    make && make install

# Download English and German language data
RUN mkdir -p /usr/local/share/tessdata && \
    cd /usr/local/share/tessdata && \
    wget https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata && \
    wget https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata

# Set library path
ENV LD_LIBRARY_PATH=/usr/local/lib

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy function code
COPY app.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler
CMD [ "app.lambda_handler" ]