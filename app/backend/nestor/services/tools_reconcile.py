"""Deterministic one-to-one reconciliation: never guess duplicate-key allocation."""
import json
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from .tools import tool
from .tools_office import _json, _out


def reconcile(a, b, tolerance='0'):
    def amount(value):
        if isinstance(value, bool) or value is None:
            raise ValueError('Số tiền thiếu hoặc không phải số.')
        try:
            number = Decimal(str(value))
        except InvalidOperation as e:
            raise ValueError('Số tiền phải được chuẩn hóa, không dùng dấu phân cách nghìn mơ hồ.') from e
        if not number.is_finite():
            raise ValueError('Số tiền phải hữu hạn.')
        return number
    tol = amount(tolerance)
    if tol < 0:
        raise ValueError('Dung sai không được âm.')
    sources = []
    for label, rows in [('A', a), ('B', b)]:
        if not isinstance(rows, list):
            raise ValueError(f'Nguồn {label} phải là mảng các dòng.')
        groups = defaultdict(list)
        for i, row in enumerate(rows, 1):
            if not isinstance(row, dict) or not str(row.get('key') or '').strip():
                raise ValueError(f'Nguồn {label}, dòng {i}: thiếu khóa; không được tự ghép.')
            groups[str(row['key']).strip()].append({'row': i, 'amount': amount(row.get('amount'))})
        sources.append(groups)
    ga, gb = sources
    output = []
    for key in sorted(ga.keys() | gb.keys()):
        left, right = ga.get(key, []), gb.get(key, [])
        if len(left) > 1 or len(right) > 1:
            status = 'ambiguous'
        elif not left:
            status = 'only_b'
        elif not right:
            status = 'only_a'
        else:
            status = 'matched' if abs(left[0]['amount'] - right[0]['amount']) <= tol else 'difference'
        sa = sum((r['amount'] for r in left), Decimal(0))
        sb = sum((r['amount'] for r in right), Decimal(0))
        output.append({'key': key, 'status': status, 'rows_a': [r['row'] for r in left], 'rows_b': [r['row'] for r in right], 'amount_a': str(sa), 'amount_b': str(sb), 'difference': str(sa - sb)})
    return {'groups': output, 'control': {'rows_a': len(a), 'rows_b': len(b), 'accounted_a': sum(len(g['rows_a']) for g in output), 'accounted_b': sum(len(g['rows_b']) for g in output), 'total_a': str(sum((amount(r['amount']) for r in a), Decimal(0))), 'total_b': str(sum((amount(r['amount']) for r in b), Decimal(0)))}, 'requires_review': any(g['status'] != 'matched' for g in output)}


@tool('reconcile_records', 'Đối chiếu hai nguồn bằng Decimal. Mỗi dòng có key và amount đã chuẩn hóa cùng đơn vị; khóa trùng không tự ghép mà đưa vào ambiguous. Xuất Excel đầy đủ nguồn, nhóm đối chiếu và tổng kiểm soát riêng mỗi nguồn. Không tự đổi số liệu.',
      {'source_a': ('string', 'JSON mảng [{"key":"CT01","amount":"100.25"}]'), 'source_b': ('string', 'JSON mảng cùng cấu trúc'), 'output_path': ('string', 'Đường dẫn .xlsx kết quả mới'), 'tolerance': ('string', 'Dung sai cùng đơn vị tiền với đầu vào, mặc định 0')}, required=['source_a', 'source_b', 'output_path'], risk='file')
def reconcile_records(ctx, source_a, source_b, output_path, tolerance='0'):
    from openpyxl import Workbook
    a, b = _json(source_a, 'Nguồn A'), _json(source_b, 'Nguồn B')
    result = reconcile(a, b, tolerance)
    path = _out(ctx, output_path, '.xlsx')
    if path.exists():
        raise ValueError('File kết quả đã tồn tại; chọn tên phiên bản mới.')
    wb = Workbook(); wb.remove(wb.active)
    for name, rows in [('Nguồn A', a), ('Nguồn B', b)]:
        ws = wb.create_sheet(name); ws.append(['Dòng nguồn', 'Khóa', 'Số tiền chuẩn hóa (chính xác)'])
        for i, r in enumerate(rows, 1):
            ws.append([i, str(r['key']), str(r['amount'])])
    ws = wb.create_sheet('Đối chiếu');ws.append(['Khóa', 'Nhóm', 'Dòng A', 'Dòng B', 'Tiền A', 'Tiền B', 'Chênh lệch'])
    for g in result['groups']:
        ws.append([g['key'], g['status'], ','.join(map(str,g['rows_a'])), ','.join(map(str,g['rows_b'])), g['amount_a'], g['amount_b'], g['difference']])
    control = wb.create_sheet('Kiểm soát');control.append(['Chỉ tiêu', 'Giá trị'])
    for k,v in result['control'].items(): control.append([k,v])
    # All user-provided cells are strings, never spreadsheet formulas.
    for sheet in wb:
        for row in sheet:
            for cell in row:
                if isinstance(cell.value, str): cell.data_type = 's'
    wb.save(path)
    return json.dumps({'path': str(path), 'control': result['control'], 'requires_review': result['requires_review'], 'ambiguous_keys': sum(g['status']=='ambiguous' for g in result['groups']), 'note': 'Số tiền được lưu dạng chuỗi thập phân để không mất chính xác; không dùng file này như sổ kế toán đã phê duyệt.'},ensure_ascii=False)
