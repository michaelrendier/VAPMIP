import sys, json
for line in open(sys.argv[1]):
    d=json.loads(line)
    if len(sys.argv)>2 and d['id'] not in sys.argv[2:]: continue
    print(f"--- {d['id']}  ({d['n_tokens']} tokens, {len(d['clauses'])} clauses)  {d['text'][:90]!r}")
    for c in d['clauses']:
        s=c['slots']
        print('  ['+c['words'][:70]+']')
        print('    SHELL',s['SHELL'].get('act'),s['SHELL'].get('polarity'),s['SHELL'].get('gap',''),'| ANCHOR',[x['w'] for x in s['ANCHOR']],'| rel',[x['lemma'] for x in s['SPAN']['relation']],'| claim',[x['w'] for x in s['SPAN']['claim']],'| frame',[[y['w'] for y in f] for f in s['SPAN']['frame']])
        print('    SCAFFOLD',[x['w'] for x in s['SCAFFOLD']],'| ELAB',[x['w'] for x in s['ELABORATE']],'| HOOK',[x['w'] for x in s['HOOK']],'| WRAP',[x['w'] for x in s['WRAP']])
    print('  content:',' '.join(c['lemma']+'/'+c['pos'][0] for c in d['content_words']))
