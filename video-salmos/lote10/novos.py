"""Folha HD só com os ids passados. Uso: novos.py cenas.json saida.jpg id1 id2 ..."""
import json, subprocess, sys
c = json.load(open(sys.argv[1])); ids = {int(x) for x in sys.argv[3:]}
json.dump([x for x in c if x["clip"]["id"] in ids], open("/tmp/claude-0/sub.json", "w"))
subprocess.run([sys.executable, "lote10/folha_hd.py", "/tmp/claude-0/sub.json", "0", "40", sys.argv[2]])
