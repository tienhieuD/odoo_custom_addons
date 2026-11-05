"""usage: legacy_view.py <module dir>  -- view syntax for versions <= 16"""
import sys
p = sys.argv[1] + '/views/dwo_model_concurrency_views.xml'
s = open(p).read()
s = s.replace('bg_color="text-bg-danger" invisible="active"', 'bg_color="bg-danger" attrs="{\'invisible\': [(\'active\', \'=\', True)]}"')
s = s.replace('domain="field_domain"', 'domain="[(\'model\', \'=\', model), (\'store\', \'=\', True), (\'readonly\', \'=\', False)]"')
open(p, 'w').write(s)
