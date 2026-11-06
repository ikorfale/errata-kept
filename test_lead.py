import pytest
from lead import lead, table

P = '2026-11-01T00:00Z'; D = '2026-11-11T00:00Z'  # horizon 240 h


def r(notice, verdict='announced_revision'):
    return {'promised': P, 'deadline': D, 'notice_at': notice, 'verdict': verdict}


def test_in_time():
    x = lead(r('2026-11-06T00:00Z'))
    assert x == {'lead_h': 120.0, 'horizon_h': 240.0, 'share': 0.5, 'label': 'in-time'}


def test_one_minute_before_is_late_notice():
    assert lead(r('2026-11-10T23:59Z'))['label'] == 'late-notice'


def test_boundary_exactly_ten_percent_is_in_time():
    assert lead(r('2026-11-10T00:00Z'))['label'] == 'in-time'  # 24 h of 240 = 0.10, not < 0.10


def test_after_deadline_is_flagged_not_counted_as_revision():
    assert lead(r('2026-11-11T02:00Z'))['label'] == 'after-deadline'


def test_naive_time_refused():
    with pytest.raises(ValueError):
        lead({'promised': '2026-11-01T00:00', 'deadline': D, 'notice_at': D})


def test_notice_before_promise_refused():
    with pytest.raises(ValueError):
        lead(r('2026-10-31T00:00Z'))


def test_table_counts_only_revision_kinds():
    rows = [r('2026-11-06T00:00Z'), r('2026-11-10T23:00Z', 'renegotiated'), {'verdict': 'kept'}]
    t = table(rows)
    assert t['announced_revision']['n'] == 1 and t['renegotiated']['late-notice'] == 1
