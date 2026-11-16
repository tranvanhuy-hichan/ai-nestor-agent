from decimal import Decimal
import pytest
from nestor.services.tools_reconcile import reconcile


def test_duplicate_keys_are_not_multiplied_or_guessed():
    result = reconcile([{'key':'a','amount':'10'},{'key':'a','amount':'20'}], [{'key':'a','amount':'30'}])
    assert result['groups'][0]['status']=='ambiguous'
    assert result['control']['accounted_a']==2
    assert result['control']['accounted_b']==1
    assert result['control']['total_a']=='30'
    assert result['requires_review']


def test_exact_decimal_and_separate_source_conservation():
    result = reconcile([{'key':'a','amount':'0.10'},{'key':'b','amount':'0.20'},{'key':'x','amount':'1'}], [{'key':'a','amount':'0.1'},{'key':'b','amount':'0.2'},{'key':'y','amount':'2'}])
    assert [g['status'] for g in result['groups']]==['matched','matched','only_a','only_b']
    assert result['control']['accounted_a']==3 and result['control']['accounted_b']==3
    assert Decimal(result['control']['total_a'])==Decimal('1.30')


@pytest.mark.parametrize('value',[None,True,'NaN','Infinity','1,000'])
def test_invalid_amounts_are_rejected(value):
    with pytest.raises(ValueError):reconcile([{'key':'a','amount':value}],[])


def test_negative_tolerance_and_missing_keys_are_rejected():
    with pytest.raises(ValueError):reconcile([],[], '-1')
    with pytest.raises(ValueError):reconcile([{'amount':'10'}],[])
