## About

This is a temporary test suite to help exercise `sevctl`'s command line
interface. It is meant to verify that:

* there aren't any crashers during `sevctl`'s normal operation
* `sevctl` emits human-readable error messages when a known failure path is
traversed
* `sevctl` emits the appropriate certificate data that is requested

As mentioned before, this test suite is temporary until some or all of these
tests are upstreamed in an appropriate fashion.

**This test suite is secondary to the automated unit tests in the `sev` crate that
`sevctl` is built upon.**

## Prerequisites

1. Install `python3`
2. Install `pytest` (`python3 -m pip install --user -r requirements.txt`)
3. Install `sevctl` to a place your shell will find it, (i.e., somewhere
   in your `$PATH`) or you can set the `SEVCTL` environment variable to
   the location of your `sevctl` binary

## Running

```console
$ SEVCTL=/path/to/sevctl pytest -rA test_sevctl.py
```

## Interpreting the results

Some tests may be disabled depending on whether or not the test suite believes
it is running on an SEV-capable machine. It will do a cursory check for the
`/dev/sev` device node and attempt to open it either in read mode or write mode
to quickly determine if SEV capabilities may be possible.

If the test suite fails that check, some tests will be skipped because
`sevctl` will fail if it's unable to utilize `/dev/sev`, meaning the test suite
will be unable to test what it wants to test.

It is recommended to run the test suite on:

1. A machine without SEV capabilities
2. A machine with a 2nd generation EPYC processor.
3. A machine with a 1st generation EPYC processor.

`pytest` will capture and emit `sevctl`'s error messages. Many of these tests
are meant to provoke `sevctl` into emitting an error. The test will not parse
the error messages; it will only check that `sevctl` did not exit with a
successful error code.

In these cases, just scan the output and make sure there are no stack
traces. `sevctl`'s error messages should be human-readable.

**The test suite passes if there are no *failed* test cases.** It is okay
if there are skipped test cases.
