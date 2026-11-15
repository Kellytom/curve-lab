"""The build line carries the clock, so a rebuild a minute later never matches.

Four page tests compare a checked-in page against a fresh build. Comparing the
stamp as well made them fail whenever the minute rolled over, with nothing
changed, which reads as a regression. The comparison is about the page.

Register row 18.
"""


def without_build_stamp(text):
    return "\n".join(line for line in text.splitlines() if 'id="n-build"' not in line)
