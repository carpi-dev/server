### carpi_server
#### what is it?
- module
    - download center
    - builder
#### why?
so it is easier to make new modules and get them distributed.
#### how to..
##### ... use
```shell script
usage: carpi_server [-h] [--host HOST] [--port PORT] [-sk SSL_KEY]
                   [-sc SSL_CERT] [-cu CREATE_USER] [-du DELETE_USER]
                   [-u USERNAME] [-db DATABASE] [--enable-login ENABLE_LOGIN]
                   [--work-dir WORK_DIR] [--output-dir OUTPUT_DIR]

optional arguments:
  -h, --help            show this help message and exit
  --host HOST
  --port PORT
  -sk SSL_KEY, --ssl-key SSL_KEY
  -sc SSL_CERT, --ssl-cert SSL_CERT
  -cu CREATE_USER, --create-user CREATE_USER
  -du DELETE_USER, --delete-user DELETE_USER
  -u USERNAME, --username USERNAME
  -db DATABASE, --database DATABASE
  --enable-login ENABLE_LOGIN
  --work-dir WORK_DIR
  --output-dir OUTPUT_DIR
```