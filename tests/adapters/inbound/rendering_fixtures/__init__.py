"""A made-up package carrying its own trace line and that line's English text.

Importing `levies` registers its renderer with `@english_renderer`, as a jurisdiction package
would; the tests import it only while the shared registry points at a fresh one.
"""
