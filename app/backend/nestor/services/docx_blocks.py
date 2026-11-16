"""Compose native Word paragraphs, lists and tables; no Markdown intermediary."""
from docx.shared import Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def text_of(blocks):
    parts=[]
    for block in blocks:
        if not isinstance(block,dict):raise ValueError('Mỗi block phải là object có type và nội dung.')
        parts.append(str(block.get('text','')))
        parts.extend(str(x) for x in block.get('items',[]))
        parts.extend(str(v) for row in block.get('rows',[]) for v in row)
        parts.extend(str(r.get('text','')) for r in block.get('runs',[]) if isinstance(r,dict))
    return '\n'.join(parts)


def validate(blocks):
    if not isinstance(blocks,list) or not blocks:raise ValueError('blocks phải là mảng nội dung không rỗng.')
    for b in blocks:
        if not isinstance(b,dict) or b.get('type') not in {'heading','paragraph','bullets','numbered','table','page_break'}:raise ValueError('Block hỗ trợ: heading, paragraph, bullets, numbered, table, page_break.')
        if b['type']=='heading' and b.get('level',1) not in (1,2,3):raise ValueError('Heading level phải là 1, 2 hoặc 3.')
        if b['type'] in ('bullets','numbered') and (not isinstance(b.get('items'),list) or not b['items'] or any(not isinstance(x,str) for x in b['items'])):raise ValueError('Danh sách cần items là mảng chuỗi không rỗng.')
        if b['type']=='table':
            rows=b.get('rows')
            if not isinstance(rows,list) or not rows or any(not isinstance(row,list) for row in rows):raise ValueError('Bảng cần rows là mảng các hàng.')
            if not rows[0] or any(len(row)!=len(rows[0]) for row in rows):raise ValueError('Các hàng bảng phải có cùng số cột, không tự bỏ ô.')
        if b['type'] in ('paragraph','heading') and not isinstance(b.get('text',''),str):raise ValueError('text phải là chuỗi.')
        if 'runs' in b and (not isinstance(b['runs'],list) or any(not isinstance(r,dict) or not isinstance(r.get('text'),str) for r in b['runs'])):raise ValueError('runs phải là mảng object có text.')


def compose(doc, blocks):
    validate(blocks)
    for b in blocks:
        kind=b['type']
        if kind=='page_break':doc.add_page_break();continue
        if kind=='heading':
            doc.add_heading(b.get('text',''),level=b.get('level',1));continue
        if kind in ('bullets','numbered'):
            for item in b['items']:
                p=doc.add_paragraph(item,style='List Bullet' if kind=='bullets' else 'List Number')
                p.paragraph_format.space_after=Pt(5)
            continue
        if kind=='paragraph':
            p=doc.add_paragraph()
            if b.get('runs'):
                for spec in b['runs']:
                    r=p.add_run(str(spec.get('text','')));r.bold=bool(spec.get('bold'));r.italic=bool(spec.get('italic'))
            else:p.add_run(b.get('text',''))
            p.paragraph_format.widow_control=True
            continue
        table=doc.add_table(rows=0,cols=len(b['rows'][0]));table.style='Table Grid'
        for index,row in enumerate(b['rows']):
            cells=table.add_row().cells
            for cell,value in zip(cells,row):
                cell.text='' if value is None else str(value)
                for p in cell.paragraphs:
                    p.paragraph_format.space_after=Pt(5);p.paragraph_format.space_before=Pt(5)
                    for r in p.runs:r.font.size=Pt(10)
                if index==0 and b.get('header',True):
                    shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'EAF0F7');cell._tc.get_or_add_tcPr().append(shade)
                    for r in cell.paragraphs[0].runs:r.bold=True
            if index==0 and b.get('header',True):
                repeat=OxmlElement('w:tblHeader');table.rows[index]._tr.get_or_add_trPr().append(repeat)
        doc.add_paragraph().paragraph_format.space_after=Pt(3)


def decorate(doc):
    # Neutral running page numbers, no invented organisation or author.
    footer=doc.sections[0].footer.paragraphs[0]
    footer.alignment=2
    r=footer.add_run();r.font.size=Pt(9)
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');r._r.addnext(field)
