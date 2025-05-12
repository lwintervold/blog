import asyncio
import itertools
import random
import time
from typing import Iterable, Awaitable

COUNTER = 0
INDEX = 0

async def foo():
    global COUNTER
    global INDEX
    INDEX += 1
    ret = INDEX
    COUNTER += 1
    print("COUNTER", COUNTER)
    val = 0.1 + random.uniform(-0.1, 0.1)
    if val < 0.19:
        await asyncio.sleep(val)
        COUNTER -= 1
        print("COUNTER", COUNTER)
    else:
        COUNTER -= 1
        print("COUNTER", COUNTER)
        raise ValueError("Operation failed")

    return ret


async def concurrent_gather(coros: Iterable[Awaitable], concurrency: int):
    to_run = enumerate(coros)
    to_return = [None for _ in range(len(coros))]

    async def runner():
        while True:
            try:
                ix, work = next(to_run)
            except StopIteration:
                return

            try:
                result = await work
            except BaseException as e:
                result = e

            to_return[ix] = result

    await asyncio.gather(*[runner() for _ in range(concurrency)])
    return to_return


async def main():
    coros = [foo() for _ in range(100)]
    result = await concurrent_gather(coros, 15)
    print(result)
    # batched = itertools.batched(coros, 15)
    # for batch in batched:
    #     await asyncio.gather(*batch)

    sleep_times = list(itertools.chain.from_iterable([[0.01, 0.01, 0.1] for _ in range(10)]))
    sleep_coros = [asyncio.sleep(t) for t in sleep_times]
    sleep_batched = itertools.batched(sleep_coros, 3)
    batch_start_time = time.monotonic()

    for sleep_batch in sleep_batched:
        await asyncio.gather(*sleep_batch)
    print("total batch time:", time.monotonic() - batch_start_time)


    concurrent_start_time = time.monotonic()
    result = await concurrent_gather([asyncio.sleep(t) for t in sleep_times], 3)
    print("total concurrent time:", time.monotonic() - concurrent_start_time)

if __name__ == "__main__":
    asyncio.run(main())
