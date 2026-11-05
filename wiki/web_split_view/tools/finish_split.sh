#!/bin/zsh
# usage: finish_split.sh <NN>  -> copy the listing assets of 19 + this version's screenshots, validate, commit, push
v=$1
M=/Users/hieu/Documents/Odoo/myproject
S=$M/odoo_custom_addons19/web_split_view/static/description
D=$M/odoo_custom_addons$v/web_split_view/static/description
O=/private/tmp/claude-501/-Users-hieu--claude/2c6103e7-e2d6-4a63-9270-126ab80a6cbe/scratchpad/split_shots/out$v
mkdir -p $D
for f in index.html flow.png icon.png banner.png; do cp $S/$f $D/$f; done
for n in 1 2 3 4; do cp $O/screenshot_$n.png $D/screenshot_$n.png; done
python3 /Users/hieu/.claude/skills/odoo-apps-listing/scripts/validate_listing.py $M/odoo_custom_addons$v/web_split_view | tail -3
cd $M/odoo_custom_addons$v
find web_split_view -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null
git add -A web_split_view && git reset -q -- 'web_split_view/**/.DS_Store' 2>/dev/null
git diff --cached --stat | tail -1
git commit -q -m "[IMP] web_split_view: automatic Split mode on every list, expand to full form, state kept, settings, OPL-1 / 39 USD, new description

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01MswwjzxQJzBYDNJzdTwzsA" && git push -q origin $(git branch --show-current) 2>&1 | tail -1
echo "$v $(git status -sb | head -1) $(git log -1 --format=%h)"
