"""Cache Word TOC page references from an actual rendered PDF; no guessed pages."""
import argparse
import sys
from pathlib import Path
import pymupdf
from docx import Document

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'reports'))
from publication_report_sections import make_contents


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--docx',type=Path,default=ROOT/'reports/Group_16_Report.docx')
    parser.add_argument('--pdf',type=Path,required=True)
    args=parser.parse_args()
    doc=Document(args.docx)
    headings=[p.text for p in doc.paragraphs if p.style.name=='Heading 1' and p.text!='Contents']
    pages={}
    with pymupdf.open(args.pdf) as pdf:
        for i,page in enumerate(pdf):
            if i<2:continue
            lines=[' '.join(x.split()) for x in page.get_text().splitlines()]
            for heading in headings:
                if ' '.join(heading.split()) in lines and heading not in pages:pages[heading]=i+1
    missing=set(headings)-pages.keys()
    if missing:raise ValueError(f'Headings missing from rendered PDF: {missing}')
    make_contents(doc,pages)
    doc.save(args.docx)
    print('Updated',len(pages),'TOC page references from',args.pdf)


if __name__=='__main__':main()
