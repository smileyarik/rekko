import json
import sys

last_user = ''
full = {}
top = []
for line in open(sys.argv[1]):
    ff = line.strip().split('\t')
    if ff[0] != last_user and last_user != '':
        top = sorted(top, key=lambda x:x[1], reverse=True)
        result = [int(x) for x,_ in top[0:20]]
        full[last_user] = result
        top = []
    last_user = ff[0]
    top.append((ff[1], float(ff[int(sys.argv[2])])))

top = sorted(top, key=lambda x:x[1], reverse=True)
result = [int(x) for x,_ in top[0:20]]
full[last_user] = result
top = []

print json.dumps(full)

