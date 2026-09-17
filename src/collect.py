"""Collect existing study outputs into one flat, shareable results folder."""
from pathlib import Path
import argparse
import html
import json
import re
import shutil
import textwrap

from .config import ROOT, WORK, RESULTS


def inline(text):
    text=html.escape(text)
    text=re.sub(r'`([^`]+)`',r'<code>\1</code>',text)
    text=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',text)
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'<a href="\2">\1</a>',text)


def render(markdown):
    blocks=[];in_code=False;in_table=False;in_list=False
    for line in markdown.splitlines():
        if line.startswith('```'):
            blocks.append('</pre>' if in_code else '<pre>');in_code=not in_code;continue
        if in_code:blocks.append(html.escape(line)+'\n');continue
        if in_table and not line.startswith('|'):blocks.append('</table>');in_table=False
        item=line.startswith(('* ','- '))
        if in_list and not item:blocks.append('</ul>');in_list=False
        if line.startswith('|'):
            if not in_table:blocks.append('<table>');in_table=True
            cells=[x.strip() for x in line.strip('|').split('|')]
            if all(re.fullmatch(r':?-+:?',x) for x in cells):continue
            blocks.append('<tr>'+''.join('<td>'+inline(x)+'</td>' for x in cells)+'</tr>');continue
        if not line:continue
        image=re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)',line)
        if image:blocks.append('<figure><img src="'+html.escape(image[2],quote=True)+'" alt="'+html.escape(image[1],quote=True)+'"></figure>');continue
        if item:
            if not in_list:blocks.append('<ul>');in_list=True
            blocks.append('<li>'+inline(line[2:])+'</li>');continue
        match=re.match(r'^(#{1,4}) (.*)',line)
        if match:
            n=len(match[1]);blocks.append(f'<h{n}>'+inline(match[2])+f'</h{n}>')
        else:blocks.append('<p>'+inline(line)+'</p>')
    if in_table:blocks.append('</table>')
    if in_list:blocks.append('</ul>')
    style='body{max-width:1100px;margin:40px auto;padding:0 24px;font:16px/1.6 system-ui;color:#172b3a}h1,h2{line-height:1.2}table{border-collapse:collapse;width:100%;font-size:14px}td{border-bottom:1px solid #ddd;padding:8px}tr:first-child{font-weight:600;background:#eef3f7}img{max-width:100%}pre{background:#f4f6f8;padding:16px;overflow:auto}code{font-size:.9em}figure{margin:24px 0}'
    return '<!doctype html><html><head><meta charset="utf-8"><title>Segmentation sensitivity study</title><style>'+style+'</style></head><body>'+''.join(blocks)+'</body></html>'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--from-results',type=Path,default=WORK,help='Existing raw study root containing analysis/ and supplied/pt002_inflow/')
    args=parser.parse_args()
    analysis=args.from_results/'analysis';supplied=args.from_results/'supplied/pt002_inflow'
    # Validate both completed studies before refreshing presentation files.
    primary=json.loads((analysis/'verification.json').read_text())
    assert primary['actual_primary_cases']==42
    supplied_checks=json.loads((supplied/'verification.json').read_text())
    assert supplied_checks['status']=='passed'
    RESULTS.mkdir(parents=True,exist_ok=True)
    for file in analysis.iterdir():
        if file.is_file() and not file.name.startswith('REPORT') and file.suffix in ['.png','.pdf','.csv','.json']:
            shutil.copy2(file,RESULTS/file.name)
    for name in ['coupled_solution.vtu','network_solution.vtu','tissue_solution.vtu']:
        shutil.copy2(supplied/name,RESULTS/name)
    for name in ['metrics.csv','verification.json']:
        shutil.copy2(supplied/name,RESULTS/('supplied_'+name))
    shutil.copy2(supplied/'input/metadata.json',RESULTS/'supplied_input_metadata.json')
    main=(analysis/'REPORT.md').read_text()
    start=main.index('## Files and reproducibility')
    main=main[:start]+'''## Files and reproducibility

* All figures, tables, and this combined report are together in this folder.
* `all_cases.csv`, `random_break_summary.csv`, and `break_intervals.csv` contain the synthetic-study measurements and gap definitions.
* The supplied-network solution and measurements appear in the supplement below.
* All runnable code is in `../src/`; instructions are in [the repository README](../README.md).
* Full per-case native meshes and raw run records remain on NOTS under `/scratch/pzz1/segmentation-sensitivity/` and in the earlier full-results archive. This compact repository retains the three supplied-network VTU solutions and all presentation figures and tables.
* The model and mesh construction code are local modules. No upstream patch is required. FEniCSx, PETSc, MPI, and fenicsx_ii are unmodified external dependencies.

'''
    supplement=(supplied/'REPORT.md').read_text().replace('scripts/','src/').replace('-m study.','-m src.')
    supplement=supplement.replace('(metrics.csv)','(supplied_metrics.csv)').replace('(verification.json)','(supplied_verification.json)')
    supplement=supplement.replace('The accompanying native XDMF/HDF5 files retain normalized coordinates.', 'Native XDMF/HDF5 files in the raw run directory retain normalized coordinates.')
    supplement=supplement.replace('Input checksums, coordinate transformation, source IDs, unmodified extracted inputs, native solutions, and both runs\' metrics are included for reproducibility.',"Input checksums and the coordinate transformation are in `supplied_input_metadata.json`; source IDs are embedded in the VTU files. Both runs' metrics are in `supplied_metrics.csv`. Unmodified extracted inputs and native XDMF/HDF5 solutions remain with the raw runs on NOTS.")
    supplement=supplement.replace('python -m src.package','python -m src.collect\npython -m src.package')
    combined=main+'\n\n'+supplement
    (RESULTS/'REPORT.md').write_text(combined)
    (RESULTS/'REPORT.html').write_text(render(combined))
    # Preserve the completed scientific figures and append text pages for the supplied run.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    from pypdf import PdfReader, PdfWriter
    from tempfile import TemporaryDirectory
    with TemporaryDirectory(prefix='seg-report-') as temporary:
        extra=Path(temporary)/'supplied.pdf'
        lines=[]
        for line in supplement.splitlines():
            if line.startswith('```'):continue
            clean=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'\1',line).replace('`','').replace('**','')
            lines.extend(textwrap.wrap(clean,100) or [''])
        with PdfPages(extra) as pdf:
            for first in range(0,len(lines),52):
                fig=plt.figure(figsize=(8.27,11.69))
                fig.text(.06,.96,'\n'.join(lines[first:first+52]),va='top',fontsize=9,family='DejaVu Sans',linespacing=1.55)
                pdf.savefig(fig);plt.close(fig)
        writer=PdfWriter()
        for source in [analysis/'REPORT.pdf',extra]:writer.append(PdfReader(source))
        with (RESULTS/'REPORT.pdf').open('wb') as f:writer.write(f)
    # Catch links left behind by flattening the result directories.
    for target in re.findall(r'(?:href|src)="([^"]+)"',(RESULTS/'REPORT.html').read_text()):
        if '://' not in target and not target.startswith('#'):
            assert (RESULTS/target).exists(),target
    print('Collected both studies in',RESULTS)


if __name__=='__main__':main()
