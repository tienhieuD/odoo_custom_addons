"""usage: legacy_cascade.py <module dir>  -- versions <= 13: no ondelete cascade (the stored related field breaks on delete)"""
import sys
d = sys.argv[1]
p = d + '/models/dwo_model_concurrency.py'
s = open(p).read().replace("index=True, ondelete='cascade')", "index=True)")
open(p, 'w').write(s)
p = d + '/tests/test_concurrency.py'
s = open(p).read()
a = s.index("    def test_deleting_the_model_deletes_the_configuration")
b = s.index("    def test_skip_context_disables_the_ping")
s = s[:a] + '''    def test_deleting_the_model_does_not_block(self):
        model = self.env['ir.model'].create({'name': 'Dwo tmp', 'model': 'x_dwo_tmp', 'state': 'manual'})
        config = self.concurrency.create({'model_id': model.id})
        model.unlink()
        self.assertFalse(config.exists() and config.model_id)

''' + s[b:]
open(p, 'w').write(s)
