#!/bin/bash
systemctl status bss_portal.service
systemctl stop bss_portal.service
systemctl status bss_portal.service
cd /scripts/bssmr_service/main
python3 manage.py migrate
systemctl status bss_portal.service
systemctl start bss_portal.service
systemctl status bss_portal.service