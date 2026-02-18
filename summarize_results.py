import json, os, glob
results_dir = 'test_results'
for f in sorted(glob.glob(os.path.join(results_dir, '*.json'))):
    name = os.path.basename(f).replace('.json','')
    try:
        d = json.load(open(f, encoding='utf-8-sig'))
        ctx = d.get('context', [])
        steps = d.get('process_steps', [])
        gen = next((s['duration'] for s in steps if 'generat' in s.get('step','').lower()), 0)
        sources = [c['source'] for c in ctx]
        avg_rel = sum(c.get('relevance',0) for c in ctx) / max(len(ctx),1)
        resp_len = len(d.get('response',''))
        print(f"{name}: resp={resp_len}, ctx={len(ctx)}, rel={avg_rel:.2f}, ms={gen:.0f}, src={sources}")
    except Exception as e:
        print(f"{name}: ERROR {e}")
