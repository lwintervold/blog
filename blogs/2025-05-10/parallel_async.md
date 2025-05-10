# Parallelism and async Python
When writing asynchronous/concurrent code, there's often a section of execution which is "embarassingly parallel". A simple example would be: "After determining a set of resource ids which we must resolve to actual resouces, look up each resource by calling another service.".

The straightforward way to do this looks like:
```
# resource_ids = [...]
resources = [await lookup(resource_id) for resource_id in resource_ids]
```

This works, but runs all lookups serially. We're using asyncio to allow us the ability to run tasks concurrently, but within the task we aren't taking advantage of that fact. An improvement can be made with the Python stdlib:

```
batch_size = 30
batched = itertools.batched(resource_ids, batch_size)

results = []
for batch in batches:
    results.extend(await asyncio.gather(*[lookup(resource_id) for resource_id in batch]))
```

This adds parallelism to the execution - assuming that `lookup()` is i/o bound, we'll have a significant speedup as we're amortizing the cost of the latency involved in the i/o operation. But there is still inefficiency here - we block the batch completion on the longest running task in the batch. For a simple example, consider the case where all tasks expect one in the batch complete in 0.1 seconds - but one task completes in 10s. During the first 0.1s, we are concurrently executing 30 tasks. Between 0.1s and 10s, we are concurrently executing 1 task. Under the assumption it is safe to execute 30 concurrent tasks, we are wasting time waiting for the last task to complete before proceeding with executing more tasks.

A better solution will be more aware of the executions of the individual tasks, and ensure we are always running with a concurrency "width" defined at the start of task execution.

An example that follows some of the semantics of `asyncio.gather()`:
```
async def concurrent_gather(coros: Iterable[Awaitable], concurrency: int):
    semaphore = asyncio.Semaphore(concurrency)
    to_run = enumerate(coros)
    to_return = [None for _ in range(len(coros))]

    async def runner():
        while True:
            async with semaphore:
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
```


Determination of truly optimal `batch_size` is difficult - generally I've simply run a simple search over different values in an attempt to optimize for lowest execution time. But understanding usage patterns of the flow at hand, and the work multiplier involved (here, a 30x multiplier) are important considerations when choosing a value.
