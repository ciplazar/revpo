RevPo
-----

RevPo is an (intentionally) over-engineered evaluator and REPL for reverse Polish (aka postfix) notation expressions (test suite included).

    In: '4 2 ** 1 +'
    Out: 17

To run the test suite:
> python revpo.py test

Or to pop straight into the REPL:
> python revpo.py

The REPL accepts postfix expressions by default, but can also handle
prefix and infix expressions if they are prefixed with `pre`/`in`
followed by a space:

    In: in (5 + ((1 + 2) * 4)) - 3
    Out: 14
