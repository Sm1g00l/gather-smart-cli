import unittest.mock as mock

import pytest


@pytest.fixture(autouse=True)
def no_real_rate_limit_wait(request):
    """Nos unitários, o 429 mockado não pode segurar a execução de verdade."""
    if request.node.get_closest_marker("e2e"):
        yield None
        return
    with mock.patch("gather_cli.webhook.time.sleep") as sleep:
        yield sleep
