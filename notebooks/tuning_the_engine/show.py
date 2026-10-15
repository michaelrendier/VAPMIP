import json,sys
for n in sys.argv[1:]:
    nb=json.load(open(f'phase_{n}.ipynb'))
    print('=====',n)
    for o in nb['cells'][-1]['outputs']:
        for l in ''.join(o.get('text','')).splitlines():
            if '[FAIL' in l or l.startswith('          ') and prev_fail or '->' in l: print(l)
            prev_fail = '[FAIL' in l
    for i,c in enumerate(nb['cells']):
        for o in c.get('outputs',[]):
            if o.get('output_type')=='error': print('ERR cell',i,o['ename'],o['evalue'][:120])
