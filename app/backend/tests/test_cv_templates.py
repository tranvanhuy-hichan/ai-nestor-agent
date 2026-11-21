"""Use the real template renderer to catch layout selection and escaping regressions."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from nestor.assistant_defs.forms import form_for
from nestor.services.tools import ToolContext, call
from nestor.services import tools_cv

RENDERER = Path(tools_cv.__file__).resolve().parents[2] / 'cv_templates' / 'render.mjs'


def render(template, data, lang='vi'):
    return subprocess.run([shutil.which('node'), str(RENDERER)], input=json.dumps({'template': template, 'data': data, 'lang': lang}), capture_output=True, text=True, timeout=30)


def test_cv_requires_explicit_template_for_both_workflows():
    for flow in form_for('cv-viec-lam')['flows']:
        creation = next(s for s in flow['steps'] if 'create_cv' in s['task'])
        selector = next(f for f in creation['fields'] if f['type'] == 'cv-template')
        assert selector['required']
        assert 'pdf' in creation['produces']


def test_renderer_uses_selected_layout_and_never_sample_profile():
    modern = render('modern', {'name': 'Nguyễn An <script>alert(1)</script>', 'title': 'Developer', 'skills': [{'name': 'Python'}]}).stdout
    executive = render('executive', {'name': 'Nguyễn An', 'title': 'Developer'}).stdout
    assert '#0ea5e9' in modern and '#1d4ed8' in executive
    assert 'Nguyễn An' in modern and '&lt;script&gt;' in modern
    assert '<script>' not in modern and 'Nguyễn Minh Anh' not in modern
    assert 'Liên hệ' in modern
    assert 'Contact' in render('modern', {'name': 'An'}, 'en').stdout
    assert modern != executive


def test_renderer_rejects_invalid_template_and_missing_name():
    assert render('not-a-template', {'name': 'An'}).returncode != 0
    assert render('modern', {}).returncode != 0


def test_cv_cannot_write_outside_session_without_approval(tmp_path):
    work = tmp_path / 'session'
    work.mkdir()
    ctx = ToolContext(workspace=work, cwd=work, approver=lambda *a: False, confirm_exec=True)
    out, ok = call(ctx, 'create_cv', {'path': str(tmp_path / 'outside.pdf'), 'template': 'modern', 'data': json.dumps({'name': 'An'})})
    assert not ok
    assert not (tmp_path / 'outside.pdf').exists()


def test_template_fields_follow_actual_layout():
    result = subprocess.run([shutil.which('node'), str(RENDERER), '--schema'], input='{}', capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    schemas = json.loads(result.stdout)
    assert len(schemas) == 146
    for template, schema in schemas.items():
        assert 'name' in [f['key'] for f in schema['contact']], template
        assert schema['sections'], template
    modern = {s['key'] for s in schemas['modern']['sections']}
    infographic = {s['key'] for s in schemas['chi-so-xanh']['sections']}
    assert 'highlights' not in modern
    assert 'highlights' in infographic
    assert schemas['modern']['photo'] is True
    assert schemas['minimal']['photo'] is False


def test_cv_profile_is_required_and_editor_respects_skipped_sections():
    for flow in form_for('cv-viec-lam')['flows']:
        creation = next(s for s in flow['steps'] if 'create_cv' in s['task'])
        assert any(f['type'] == 'cv-profile' and f['required'] for f in creation['fields'])
        assert 'skipped_sections' in creation['task']
        assert 'không nâng khống' in creation['task']


def test_cv_template_picker_is_first_field_in_both_entry_flows():
    for flow in form_for('cv-viec-lam')['flows']:
        first = flow['steps'][0]['fields'][0]
        assert first['key'] == 'mau_cv'
        assert first['type'] == 'cv-template' and first['required']


def test_long_cv_is_not_silently_truncated():
    data = {
        'name': 'An',
        'summary': 'Nội dung giới thiệu. ' * 100 + 'END_SUMMARY',
        'experience': [{'role': f'Role {i}', 'company': f'Company {i}', 'desc': 'Chi tiết công việc. ' * 100 + f'END_EXP_{i}'} for i in range(15)],
        'projects': [{'name': f'Project {i}', 'desc': 'Chi tiết dự án. ' * 80 + f'END_PROJECT_{i}'} for i in range(11)],
        'awards': 'Chứng chỉ chuyên môn. ' * 70 + 'END_AWARDS',
        'skills': [{'name': f'SKILL_{i}'} for i in range(25)],
    }
    result = render('modern', data)
    assert result.returncode == 0, result.stderr
    assert 'END_SUMMARY' in result.stdout and 'END_AWARDS' in result.stdout
    for i in range(15):
        assert f'END_EXP_{i}' in result.stdout
    for i in range(11):
        assert f'END_PROJECT_{i}' in result.stdout
    assert 'SKILL_24' in result.stdout


def test_incomplete_edit_is_rejected_instead_of_silently_printing_raw_input():
    from nestor.services.cv_content import preserve_profile, IncompleteCvError
    profile = {'template': 'modern', 'skipped_sections': [], 'data': {'name': 'An',
        'projects': [{'id': 'p1', 'name': 'One', 'desc': 'Built 12 integrations.'}, {'id': 'p2', 'name': 'Two', 'desc': 'Developed a dashboard.'}]}}
    with pytest.raises(IncompleteCvError, match='CHƯA xuất file'):
        preserve_profile(profile, {'projects': []})
    with pytest.raises(IncompleteCvError, match='thiếu số liệu'):
        preserve_profile(profile, {'projects': [{'id': 'p1', 'name': 'One', 'desc': 'Built integrations.'}, {'id': 'p2', 'name': 'Two', 'desc': 'Designed and developed an accessible dashboard.'}]})


def test_concise_rewrite_and_skill_corrections_are_not_replaced_with_raw_text():
    from nestor.services.cv_content import preserve_profile
    original = 'I worked on developing and implementing ' + 'customer integration features ' * 12 + 'for 12 customer systems.'
    profile = {'template': 'modern', 'skipped_sections': [], 'data': {'name': 'An',
        'experience': [{'id': 'e1', 'role': 'Engineer', 'company': 'ACME', 'desc': original}],
        'skills': [{'id': 's1', 'name': 'Devopts, Docker, Linux'}]}}
    rewrite = 'Developed and maintained integrations for 12 customer systems.'
    output, _ = preserve_profile(profile, {'experience': [{'id': 'e1', 'desc': rewrite}], 'skills': [{'id': 's1', 'name': 'DevOps, Docker và Linux'}]})
    assert output['experience'][0]['desc'] == rewrite
    assert output['skills'][0]['name'] == 'DevOps, Docker và Linux'


def test_no_photo_portfolio_does_not_render_oversized_initials_placeholder():
    result = render('anh-lon-den', {'name': 'Nguyễn Văn An', 'title': 'Engineer', 'skills': [{'name': 'Python'}]})
    assert result.returncode == 0
    assert 'height:16em' not in result.stdout
    assert 'font-size:4.5em' not in result.stdout
    assert 'Python' in result.stdout and 'Nguyễn Văn An' in result.stdout


def test_editor_can_improve_wording_and_reorder_without_reassigning_entries():
    from nestor.services.cv_content import preserve_profile
    profile = {'template': 'modern', 'skipped_sections': [], 'data': {'name': 'An', 'projects': [
        {'id': 'p1', 'name': 'One', 'desc': 'Built 12 integrations.'}, {'id': 'p2', 'name': 'Two', 'desc': 'Built a customer dashboard.'}]}}
    output, _ = preserve_profile(profile, {'projects': [
        {'id': 'p2', 'name': 'Two', 'desc': 'Designed and built a customer dashboard with accessible interface components.'},
        {'id': 'p1', 'name': 'One', 'desc': 'Designed, built and maintained 12 reliable integrations with customer systems.'}]})
    assert output['projects'][0]['id'] == 'p1' and '12 reliable' in output['projects'][0]['desc']
    assert output['projects'][1]['id'] == 'p2' and 'accessible' in output['projects'][1]['desc']


def test_original_profile_is_read_from_user_history_not_model_generated_data():
    from nestor.services.cv_content import profile_from_messages
    source = {'template': 'modern', 'data': {'name': 'An', 'projects': [{'name': 'Keep me'}]}, 'skipped_sections': []}
    messages = [{'role': 'user', 'content': '- Profile: ' + json.dumps(source)},
                {'role': 'assistant', 'content': '- Profile: ' + json.dumps({**source, 'data': {'name': 'Wrong'}})},
                {'role': 'user', 'content': 'Please fix the missing projects.'}]
    assert profile_from_messages(messages) == source
