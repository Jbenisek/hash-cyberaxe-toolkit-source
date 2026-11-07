from common import *
import json
print(json.dumps(validate(), indent=1))
b = base(); print(b["time"], b["mem"], b["score"], b["per_body"], b["tmax"])
lg = rho.ledger(256); print(log2(lg["total"]/638), lg["total"] == b["total"])
