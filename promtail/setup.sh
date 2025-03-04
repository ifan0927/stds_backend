#!/bin/sh

# 用環境變數替換配置文件中的佔位符
sed -i "s/LOKI_HOST/${LOKI_HOST}/g" /etc/promtail/promtail-config.yml
sed -i "s/LOKI_PORT/${LOKI_PORT}/g" /etc/promtail/promtail-config.yml

# 執行 Promtail
/usr/bin/promtail -config.file=/etc/promtail/promtail-config.yml