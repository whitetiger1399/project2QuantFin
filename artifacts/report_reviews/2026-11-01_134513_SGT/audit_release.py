import json, hashlib, re, subprocess
from pathlib import Path
import pymupdf
root=Path.cwd(); out=root/'artifacts/report_reviews/2026-11-01_134513_SGT'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def verify(p):
 m=json.loads(p.read_text()); rows=[]
 for group,base in [('files',p.parent),('inputs',root),('input_hashes',root)]:
  for k,v in m.get(group,{}).items():
   f=base/k; actual=sha(f) if f.is_file() else None
   rows.append(dict(group=group,path=str(f.relative_to(root)),expected=v,actual=actual,passed=actual==v))
 return dict(manifest=str(p.relative_to(root)),manifest_sha256=sha(p),checks=len(rows),failed=[r for r in rows if not r['passed']],passed=sum(r['passed'] for r in rows))
ids=['ai_capability_panel_20261101T012801Z_ff277b55597d727a','ai_capability_2026_panel_20261101T012848Z_7f83e6f3f4f128f8','cm_ai_capability_screening_20261101T013231Z_038064c84d36','cm_ai_capability_confirmation_20261101T020346Z_327cf6e7c3bd','cm_ai_capability_final_test_20261101T025817Z_30ebf00d8090','cm_ai_capability_2026_forward_20261101T030225Z_6a066bcfcc82','hypotheses_20261101T030841Z_d494c2f238ca64a6','model_evidence_final_test_20261101T030544Z_a4d9077ee46e','model_evidence_forward_extension_2026_20261101T030629Z_2f2c1a45c5fc','ai_strategy_comparison_20261101T030717Z_591c864e3aba','ai_strategy_comparison_20261101T030726Z_9660a3a84bc3']
paths=[]
for base in ['artifacts','data/processed']:
 for p in (root/base).rglob('manifest.json'):
  if p.parent.name in ids:paths.append(p)
paths.append(root/'reports/publication_figure_pack_2026-11-01/manifest.json')
a=[verify(p) for p in paths]
qa=json.loads((root/'reports/report_publication_verification.json').read_text());reports=[]
for name,v in qa['files'].items():reports.append(dict(path='reports/'+name,expected=v,actual=sha(root/'reports'/name),passed=v==sha(root/'reports'/name)))
pdf=pymupdf.open(root/'reports/Project2_Team16_Report.pdf')
result=dict(review_baseline_sgt='2026-11-01T13:45:13+08:00',git_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),manifest_checks=a,publication_files=reports,pdf_pages=len(pdf),recorded_pdf_pages=qa['pages'],contents_page_text=pdf[1].get_text())
print(json.dumps(result,indent=2))
