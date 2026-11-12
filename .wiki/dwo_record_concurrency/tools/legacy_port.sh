#!/bin/zsh
# usage: legacy_port.sh <NN>  -- copy the 15.0 module to <NN> (14, 13, 12) and adapt manifest/assets
v=$1
M=$HOME/Documents/Project/odoo_appstore
rm -rf $M/odoo_custom_addons$v/dwo_record_concurrency
rsync -a --exclude __pycache__ --exclude .DS_Store $M/odoo_custom_addons15/dwo_record_concurrency/ $M/odoo_custom_addons$v/dwo_record_concurrency/
cd $M/odoo_custom_addons$v/dwo_record_concurrency
python3 - $v <<'EOF'
import sys,re
v=sys.argv[1]
s=open('__manifest__.py').read()
s=s.replace('"version": "15.0.1.1.0"', f'"version": "{v}.0.1.1.0"')
s=re.sub(r'    "assets": \{.*?\n    \},\n', '', s, flags=re.S)
s=s.replace('        "views/menu.xml",\n','        "views/menu.xml",\n        "views/assets.xml",\n')
open('__manifest__.py','w').write(s)
open('views/assets.xml','w').write('''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <template id="assets_backend" name="Record Concurrency Guard assets" inherit_id="web.assets_backend">
        <xpath expr="//script[last()]" position="after">
            <script type="text/javascript" src="/dwo_record_concurrency/static/src/js/concurrency.js"/>
        </xpath>
    </template>

    <template id="assets_tests" name="Record Concurrency Guard tours" inherit_id="web.assets_tests">
        <xpath expr="." position="inside">
            <script type="text/javascript" src="/dwo_record_concurrency/static/tests/tours/concurrency_tour.js"/>
        </xpath>
    </template>
</odoo>
''')
EOF
python3 /tmp/legacy_tests.py $v 2>/dev/null || true
grep -n '"version"\|assets.xml\|"assets"' __manifest__.py
