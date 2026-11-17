# Security policy

## Supported versions

tax-engine is pre-1.0. Security fixes are made on the `main` branch and published as a new release on [PyPI](https://pypi.org/project/tax-engine/). Only the latest release is supported.

## Reporting a vulnerability

Please report security problems privately. Do not open a public issue or pull request for them.

Use GitHub's private vulnerability reporting: open the repository's **Security** tab and choose **Report a vulnerability**. Only the maintainers can see the report.

Please include:

- what you found and which part of the code it affects,
- steps or a small example that reproduces it,
- the version or commit you tested.

## What to expect

We will acknowledge a report as soon as we can, work with you to confirm and fix the problem, and credit you in the fix if you wish. Please give us a reasonable chance to release a fix before you disclose the problem publicly.

## What counts as a security issue

Examples: code execution or file access triggered by crafted input or dataset files, unsafe parsing of manifests or datasets, and dependency vulnerabilities that affect users of the library.

Wrong tax results are not security issues. Report those as ordinary issues, with the inputs and the form line involved.
