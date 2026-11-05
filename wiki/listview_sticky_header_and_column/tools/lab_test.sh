#!/bin/zsh
# usage: lab_test.sh <NN> <srcdir>   (env: EXTRA, WRAP)
v=$1; src=$2
export WRAP_PORT=83$v
export ODOO_BROWSER_BIN=/private/tmp/claude-501/-Users-hieu--claude/2c6103e7-e2d6-4a63-9270-126ab80a6cbe/scratchpad/cft/shell/chrome-headless-shell-mac-arm64/chrome-headless-shell
docker exec postgres179 dropdb -U odoo --if-exists lab${v}t 2>/dev/null; docker exec postgres179 createdb -U odoo lab${v}t
cd /Users/hieu/Documents/Odoo/$src
perl -e 'alarm 560; exec @ARGV' ./venv/bin/python ${WRAP:-odoo-bin} -c ../myproject/odoo_custom_addons${v}_conf/odoo.conf -d lab${v}t -i listview_sticky_test_lab $EXTRA --test-tags /listview_sticky_test_lab --stop-after-init --http-port=83$v > /tmp/lab$v.log 2>&1
echo "exit=$? errors=$(grep -cE ' (ERROR|CRITICAL) ' /tmp/lab$v.log) succeeded=$(grep -cE 'tour succeeded|test successful' /tmp/lab$v.log) labfail=$(grep -c LABFAIL /tmp/lab$v.log)"
grep -nE "LABFAIL|Traceback|ParseError|Invalid|Error:" /tmp/lab$v.log | cut -c1-260 | head -8
echo "tables: $(docker exec postgres179 psql -U odoo -d lab${v}t -Atc "select count(*) from information_schema.tables where table_name like 'lshc%' and table_type='BASE TABLE'")  views: $(docker exec postgres179 psql -U odoo -d lab${v}t -Atc "select count(*) from information_schema.tables where table_name like 'lshc%' and table_type='VIEW'")"
docker exec postgres179 dropdb -U odoo --if-exists lab${v}t
