Labels: ready-for-agent
Status: in-progress

## Description

Ticket 25 declared `license = "MIT"` and kept the matching classifier
`"License :: OSI Approved :: MIT License"`. Current setuptools rejects that pair
under PEP 639, which superseded license classifiers with SPDX license
expressions:

```
setuptools.errors.InvalidConfigError: License classifiers have been superseded
by license expressions (see https://peps.python.org/pep-0639/). Please remove:
License :: OSI Approved :: MIT License
```

`tests/test_packaging.py` therefore fails before it builds the wheel, so the
suite is red and `0.1.0` cannot be packaged. The metadata also asks only for
`setuptools>=64`, while the `license = "MIT"` string form needs the PEP 639
support that setuptools 77 added.

The fix is to drop the classifier and raise the build requirement; the license
itself does not change.

## Blocked by

None.

## Acceptance criteria

- [ ] `pyproject.toml` declares `license = "MIT"` and carries no `License ::` classifier.
- [ ] The build-system requirement names a setuptools that supports PEP 639 (`>=77`).
- [ ] `py -3.14 -m unittest tests.test_packaging -v` passes.
- [ ] The whole suite passes: `py -3.14 -m unittest discover -s tests -t . -v`.
- [ ] `py -3.14 tools/check_payload_sync.py` exits 0.

## Out of scope

- Changing the license itself or the `LICENSE` file.
- Any other packaging metadata or dependency change.
