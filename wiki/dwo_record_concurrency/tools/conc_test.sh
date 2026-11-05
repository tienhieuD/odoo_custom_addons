#!/bin/zsh
# usage: conc_test.sh <NN> <srcdir> [extra odoo args...]   (runs install + tests of dwo_record_concurrency)
v=$1; src=$2; shift 2
export ODOO_BROWSER_BIN=/private/tmp/claude-501/-Users-hieu--claude/2c6103e7-e2d6-4a63-9270-126ab80a6cbe/scratchpad/cft/shell/chrome-headless-shell-mac-arm64/chrome-headless-shell
export WRAP_PORT=83$v
docker exec postgres179 dropdb -U odoo --if-exists conc${v}t 2>/dev/null; docker exec postgres179 createdb -U odoo conc${v}t
cd /Users/hieu/Documents/Odoo/$src
perl -e 'alarm 560; exec @ARGV' ./venv/bin/python ${WRAP:-odoo-bin} -c ../myproject/odoo_custom_addons${v}_conf/odoo.conf -d conc${v}t -i ${INSTALL:-dwo_record_concurrency} $@ --test-tags /dwo_record_concurrency --stop-after-init --http-port=83$v > /tmp/conc$v.log 2>&1
echo "exit=$? tours_ok=$(grep -c "tour succeeded" /tmp/conc$v.log) skipped=$(grep -c " skipped " /tmp/conc$v.log) $(grep -E 'post-tests|failed, ' /tmp/conc$v.log | sed 's/.*INFO [a-z0-9]* //' | cut -c1-120 | tr '\n' ' ')"
grep -nE "^(FAIL|ERROR):|FAILED:|Traceback|ParseError|Invalid|TIMEOUT" /tmp/conc$v.log | cut -c1-250 | head -12
docker exec postgres179 dropdb -U odoo --if-exists conc${v}t
