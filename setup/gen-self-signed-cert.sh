#!/bin/bash
openssl genrsa -out ../data/crackmapexec.key 2048
openssl req -new -x509 -days 3650 -key ../data/crackmapexec.key -out ../data/crackmapexec.crt -subj "/"
