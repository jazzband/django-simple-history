from os.path import commonprefix
from typing import Any, Tuple


class ObjDiffDisplay:
    """
    A class grouping functions and settings related to displaying the textual
    difference between two (or more) objects.
    ``common_shorten_repr()`` is the main method for this.

    The code is based on
    https://github.com/python/cpython/blob/v3.12.0/Lib/unittest/util.py#L8-L52.
    """

    def __init__(
        self,
        *,
        max_length=80,
        placeholder_len=12,
        min_begin_len=5,
        min_end_len=5,
        min_common_len=5,
    ):
        self.max_length = max_length
        self.placeholder_len = placeholder_len
        self.min_begin_len = min_begin_len
        self.min_end_len = min_end_len
        self.min_common_len = min_common_len
        self.min_diff_len = max_length - (
            min_begin_len
            + placeholder_len
            + min_common_len
            + placeholder_len
            + min_end_len
        )
        assert self.min_diff_len >= 0  # nosec

    def common_shorten_repr(self, *args: Any) -> Tuple[str, ...]:
        """
        Returns ``args`` with each element converted into a string representation.
        If any of the strings are longer than ``self.max_length``, they're all shortened
        so that the first differences between the strings (after a potential common
        prefix in all of them) are lined up.
        """
        args = tuple(map(self.safe_repr, args))
        maxlen = max(map(len, args))
        if maxlen <= self.max_length:
            return args

        prefix = commonprefix(args)
        prefixlen = len(prefix)

        common_len = self.max_length - (
            maxlen - prefixlen + self.min_begin_len + self.placeholder_len
        )
        if common_len > self.min_common_len:
            assert (
                self.min_begin_len
                + self.placeholder_len
                + self.min_common_len
                + (maxlen - prefixlen)
                < self.max_length
            )  # nosec
            prefix = self.shorten(prefix, self.min_begin_len, common_len)
            return tuple(prefix + s[prefixlen:] for s in args)

        prefix = self.shorten(prefix, self.min_begin_len, self.min_common_len)
        return tuple(
            prefix + self.shorten(s[prefixlen:], self.min_diff_len, self.min_end_len)
            for s in args
        )

    def safe_repr(self, obj: Any, short=False) -> str:
        try:
            result = repr(obj)
        except Exception:
            result = object.__repr__(obj)
        if not short or len(result) < self.max_length:
            return result
        return result[: self.max_length] + " [truncated]..."

    def shorten(self, s: str, prefixlen: int, suffixlen: int) -> str:
        skip = len(s) - prefixlen - suffixlen
        if skip > self.placeholder_len:
            s = "%s[%d chars]%s" % (s[:prefixlen], skip, s[len(s) - suffixlen:])
        return s
