from docx import Document
from openpyxl import Workbook
from argus.services.deliverable_quality import inspect_file, snapshot, changed_issues


def test_docx_stub_and_missing_sections_fail(tmp_path):
    path=tmp_path/'report.docx';d=Document();d.add_heading('Báo cáo',0);d.add_paragraph('Hoạt động tốt.');d.save(path)
    result=inspect_file(path,['Phân tích','Kiến nghị'],min_words=100)
    assert not result['passed'] and len(result['errors'])==3


def test_content_tables_and_required_sections_are_read(tmp_path):
    path=tmp_path/'report.docx';d=Document();d.add_heading('Phân tích',1)
    d.add_paragraph('Dữ liệu nguồn được đối chiếu theo từng nhóm, các sai lệch chưa có xác nhận được liệt kê riêng để đơn vị xử lý.')
    t=d.add_table(rows=1,cols=1);t.cell(0,0).text='Kiến nghị: kiểm tra nguồn và xác nhận các dòng chênh lệch trước khi phê duyệt.';d.save(path)
    assert inspect_file(path,['Phân tích','Kiến nghị'])['passed']


def test_empty_workbook_and_broken_formula_fail(tmp_path):
    path=tmp_path/'table.xlsx';w=Workbook();w.active.append(['Tên','Số tiền']);w.save(path)
    assert not inspect_file(path)['passed']
    assert inspect_file(path,allow_template=True)['passed']
    w.active.append(['A','=SUM(#REF!)']);w.save(path)
    assert not inspect_file(path)['passed']


def test_formulas_are_not_claimed_recalculated_and_old_files_ignored(tmp_path):
    path=tmp_path/'table.xlsx';w=Workbook();w.active.append(['Tên','Số tiền']);w.active.append(['A',10]);w.active.append(['Tổng','=SUM(B2:B2)']);w.save(path)
    result=inspect_file(path)
    assert result['passed'] and result['warnings']
    before=snapshot(tmp_path)
    assert not changed_issues(tmp_path,before)
    bad=Document();bad.add_heading('Chưa hoàn thiện',0);bad.save(tmp_path/'stub.docx')
    assert len(changed_issues(tmp_path,before))==1


def test_unreadable_artifact_is_not_reported_complete(tmp_path):
    path=tmp_path/'broken.pdf';path.write_text('Not PDF')
    assert not inspect_file(path)['passed']


def test_agent_requests_repair_before_accepting_a_stub(tmp_env, monkeypatch):
    from argus.services import agent, sessions, assistants, workfiles
    from argus.core import config
    stage = {'n':0}
    class Fake:
        def stream(self,messages,tool_defs,effort=None):
            n=stage['n'];stage['n']+=1
            if n in (0,2):
                content='Rất tốt.' if n==0 else 'Phân tích dựa trên dữ liệu nguồn đã cung cấp. Các kết quả được đối chiếu theo từng nhóm, nêu rõ nguyên nhân chênh lệch và các bước xử lý tiếp theo để người phụ trách xác nhận.'
                calls=[{'id':f'c{n}','name':'create_docx','args':{'path':'report.docx','blocks':__import__('json').dumps([{'type':'paragraph','text':content}])}}]
            else: calls=[]
            yield {'type':'final','content':'' if calls else 'Đã hoàn tất.','tool_calls':calls,'usage':{'prompt':1,'completion':1}}
    monkeypatch.setattr(agent,'make_provider',lambda cfg:Fake())
    sid=sessions.create('Viết báo cáo');sessions.set_assistant(sid,'viet-bai-nghien-cuu')
    events=[]
    agent.run_turn(sid,'Viết báo cáo',None,lambda *a:True,events.append,tool_allow=assistants.tool_allow('viet-bai-nghien-cuu'))
    assert stage['n']==4
    assert any(e['type']=='notice' for e in events)
    assert not any(e['type']=='error' for e in events)
    assert inspect_file(workfiles.workdir_for(config.load(),sid)/'report.docx')['passed']
