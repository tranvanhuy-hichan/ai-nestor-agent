from nestor.assistant_defs.experience import CONTRACTS
from nestor.assistant_defs.forms import FORMS, form_for, validate_form


def test_curated_workflows_have_domain_intake_and_handoff_without_mutating_source():
    assert len(CONTRACTS) == 17
    for aid in CONTRACTS:
        first = form_for(aid)
        second = form_for(aid)
        assert first == second
        assert not validate_form(aid, first)
        assert first['experience']['checks']
        assert first['experience']['handoff']
        for flow in first['flows']:
            assert 'Trước khi làm:' in flow['steps'][0]['task']
            assert 'Bàn giao cuối:' in flow['steps'][-1]['task']
            for step in flow['steps']:
                if step['produces']:
                    assert 'Bảo toàn đầu vào:' in step['task']
        assert 'experience' not in FORMS[aid]
