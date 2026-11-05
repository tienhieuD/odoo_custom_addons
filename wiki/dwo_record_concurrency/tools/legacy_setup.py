"""usage: legacy_setup.py <module dir> -- setUpClass(cls) -> setUp(self) (no class-level env before 15)"""
import re, sys
for name in ('test_concurrency.py', 'test_concurrency_tour.py'):
    p = sys.argv[1] + '/tests/' + name
    s = open(p).read()
    m = re.search(r"    @classmethod\n    def setUpClass\(cls\):\n        super\(\).setUpClass\(\)\n(.*?)\n(?=    def |\Z)", s, flags=re.S)
    body = m.group(1).replace('cls.', 'self.').replace('cls)', 'self)')
    s = s[:m.start()] + "    def setUp(self):\n        super().setUp()\n" + body + "\n" + s[m.end():]
    open(p, 'w').write(s)
