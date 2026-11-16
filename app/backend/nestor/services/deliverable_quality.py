"""Inspect actual artifacts. Structural checks do not prove factual correctness."""
import re
from pathlib import Path
import unicodedata

EXTENSIONS = {'.docx', '.xlsx', '.pdf'}


def fold(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s.casefold().replace('đ','d')) if not unicodedata.combining(c))


def inspect_file(path, required_sections=(), min_words=20, allow_template=False):
    path = Path(path)
    errors, warnings, metrics = [], [], {}
    text = ''
    try:
        if path.suffix.lower() == '.docx':
            from docx import Document
            doc = Document(path)
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            cells = [c.text for t in doc.tables for r in t.rows for c in r.cells]
            text = '\n'.join(paragraphs + cells)
            metrics.update(paragraphs=len(paragraphs), tables=len(doc.tables))
        elif path.suffix.lower() == '.xlsx':
            from openpyxl import load_workbook
            wb = load_workbook(path, read_only=True, data_only=False)
            try:
                sheets = []
                for sheet in wb:
                    rows = [list(r) for r in sheet.iter_rows(values_only=True) if any(v is not None and str(v).strip() for v in r)]
                    values = [v for r in rows for v in r if v is not None]
                    formulas = [v for v in values if isinstance(v,str) and v.startswith('=')]
                    sheets.append({'name':sheet.title,'nonempty_rows':len(rows),'formulas':len(formulas)})
                    if any(str(v) in {'#REF!','#DIV/0!','#VALUE!','#NAME?','#NUM!','#N/A'} or isinstance(v,str) and v.startswith('=') and '#REF!' in v for v in values): errors.append(f'{sheet.title}: có lỗi ô hoặc tham chiếu công thức')
                    if len(rows) <= 1 and not allow_template: warnings.append(f'{sheet.title}: chỉ có tiêu đề hoặc chưa có dữ liệu')
                    text += '\n' + sheet.title + '\n' + '\n'.join(str(v) for v in values)
                metrics['sheets'] = sheets
                if not allow_template and not any(s['nonempty_rows'] > 1 for s in sheets): errors.append('Workbook chỉ có khung/tiêu đề, chưa có nội dung hoặc dữ liệu')
                if any(s['formulas'] for s in sheets): warnings.append('Có công thức; kiểm tra cấu trúc không thay thế tính lại và đối chiếu số nguồn')
            finally: wb.close()
        elif path.suffix.lower() == '.pdf':
            from pypdf import PdfReader
            pdf = PdfReader(path)
            metrics['pages'] = len(pdf.pages)
            if not pdf.pages: errors.append('PDF không có trang')
            text = '\n'.join(p.extract_text() or '' for p in pdf.pages)
            if not text.strip() and any(len(p.images) for p in pdf.pages): warnings.append('PDF chứa ảnh: cần đọc ảnh/OCR để xác nhận nội dung');min_words=0
        else:
            raise ValueError('Chỉ hỗ trợ .docx, .xlsx, .pdf')
    except Exception as e:
        return {'path':str(path),'passed':False,'errors':[f'Không đọc được file: {type(e).__name__}: {e}'],'warnings':[], 'metrics':{}}
    words = len(re.findall(r'\S+',text))
    metrics['words'] = words
    if path.suffix.lower() != '.xlsx' and words < min_words and not allow_template: errors.append(f'Nội dung quá sơ sài: {words} từ, yêu cầu tối thiểu {min_words}; cần viết đủ ý thực chất, không chèn chữ cho dài')
    for section in required_sections:
        if fold(str(section)) not in fold(text): errors.append(f'Thiếu phần yêu cầu: {section}')
    if re.search(r'\b(?:TODO|TBD)\b|\[điền[^\]]*\]|\[bổ sung[^\]]*\]',text,re.I) and not allow_template: errors.append('Còn chỉ dẫn giữ chỗ chưa được hoàn thiện')
    if re.search(r'…{1,}|\.{4,}',text): warnings.append('Có chỗ trống/dấu chấm chờ; liệt kê để người dùng xác nhận, không tự bịa để điền')
    return {'path':str(path),'passed':not errors,'errors':errors,'warnings':warnings,'metrics':metrics}


def snapshot(root):
    return {p: (p.stat().st_mtime_ns,p.stat().st_size) for p in Path(root).rglob('*') if p.is_file() and not p.is_symlink() and p.suffix.lower() in EXTENSIONS and 'uploads' not in p.relative_to(root).parts}


def changed_issues(root, before, allow_template=False):
    issues = []
    for path, sig in snapshot(root).items():
        if before.get(path) != sig:
            report = inspect_file(path, allow_template=allow_template)
            if not report['passed']: issues.append({'path':str(path.relative_to(root)),'errors':report['errors']})
    return issues
