"""Use the real template renderer to catch layout selection and escaping regressions."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from argus.assistant_defs.forms import form_for
from argus.services.tools import ToolContext, call
from argus.services import tools_cv

RENDERER = Path(tools_cv.__file__).resolve().parents[1] / 'cv_templates' / 'render.mjs'


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
