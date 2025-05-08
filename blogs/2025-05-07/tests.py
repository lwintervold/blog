import asyncio
import contextlib
import functools
import time

import pytest

def make_async(func):
    if asyncio.iscoroutinefunction(func):
        return func

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper

@contextlib.contextmanager
def log_follower_ctxmgr(path: str, drop_prior=False):
    with open(path, 'r') as file:
        if drop_prior:
            # Discard logs from other tests
            file.readlines()

        def log_follower_closure():
            return "".join(file.readlines())

        yield log_follower_closure


@pytest.fixture
def log_follower():
    with log_follower_ctxmgr('/tmp/example-out/example.log') as log_follower:
        yield log_follower


async def wait_for_log(expected: str, func, max_wait=5) -> str:
    func = make_async(func)
    logs = []
    start_time = time.monotonic()
    while time.monotonic() - start_time < max_wait:
        result = await func()
        logs.append(result)
        if expected in result:
            return "".join(logs)

        await asyncio.sleep(0.2)

    raise AssertionError(f"Failed to find {expected} within {max_wait}s")


@pytest.mark.asyncio
async def test_logging(log_follower):
    await wait_for_log("Hello from the logger", log_follower)
