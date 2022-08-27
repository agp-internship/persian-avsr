mkdir log                       && \
mkdir -p geckodriver               && \
wget https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-linux64.tar.gz -O ./geckodriver/geckodriver.tar.gz && \
tar -zxf ./geckodriver/geckodriver.tar.gz -C ./geckodriver/ && \
chmod +x geckodriver
