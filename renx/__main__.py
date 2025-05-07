from os.path import dirname, join
from os import rename
from .scantree import ScanTree
import unicodedata


def text_to_ascii(text):
    """
    Converts a Unicode string to its closest ASCII equivalent by removing
    accent marks and other non-ASCII characters.
    """
    return "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )


class App(ScanTree):
    def __init__(self) -> None:
        self._entry_filters = []
        super().__init__()

    def add_arguments(self, ap):
        self.dry_run = True
        self.bottom_up = True
        self.excludes = []
        self.includes = []
        ap.add_argument("--subs", "-s", action="append", default=[], help="subs regex")
        ap.add_argument("--lower", action="store_true", help="to lower case")
        ap.add_argument("--upper", action="store_true", help="to upper case")
        ap.add_argument(
            "--urlsafe", action="store_true", help="only urlsafe characters"
        )
        if not ap.description:
            ap.description = "Renames files matching re substitution pattern"

        super(App, self).add_arguments(ap)

    def start(self):
        from re import compile as regex
        import re

        _subs = []

        if self.lower:
            assert not self.upper, f"lower and upper conflict"
            _subs.append((lambda name, parent: name.lower()))

        if self.upper:
            assert not self.lower, f"lower and upper conflict"
            _subs.append((lambda name, parent: name.upper()))

        if self.urlsafe:
            from os.path import splitext

            def slugify(value):
                value = str(value)
                value = text_to_ascii(value)
                value = re.sub(r"[^a-zA-Z0-9_.+-]+", "_", value)
                return value

            def clean(value):
                value = str(value)
                value = re.sub(r"\-+", "-", value).strip("-")
                value = re.sub(r"_+", "_", value).strip("_")
                return value

            def urlsafe(name, parent):
                s = slugify(name)
                if s != name or re.search(r"[_-]\.", s) or re.search(r"[_-]+", s):
                    assert slugify(s) == s
                    stem, ext = splitext(s)
                    return clean(stem) + ext
                return name

            _subs.append(urlsafe)

        def _append(rex, rep):
            # print("REX", rex, rep)
            _subs.append((lambda name, parent: rex.sub(rep, name)))

        for s in self.subs:
            a = s[1:].split(s[0], 3)
            if len(a) < 2:
                raise RuntimeError("Invalid subtitue pattern `%s'" % s)
            f = 0
            if len(a) > 2:
                for x in a[2]:
                    u = x.upper()
                    if u in "AILUMSXT":
                        f |= getattr(re, u)
                    else:
                        raise RuntimeError(f"Invalid re flag {x!r}")
            if not a[0]:
                raise RuntimeError(f"Empty search pattern {s!r}'")
            rex = regex(a[0], f)
            rep = a[1]
            _append(rex, rep)

        self._subs = _subs
        super().start()

    def process_entry(self, de):

        name1 = de.name
        name2 = name1
        parent = dirname(de.path)
        dry_run = self.dry_run

        for fn in self._subs:
            v = fn(name2, parent)
            # print("PE_subs", de.path, name2, v)
            if v:
                name2 = v
        # print("PE", de.path, [name1, name2])
        if name2 and (name1 != name2):
            try:
                path = join(parent, name1)
                dry_run is False and rename(path, join(parent, name2))
            finally:
                print(f'REN: {name1!r} -> {name2!r} {dry_run and "?" or "!"} @{parent}')


(__name__ == "__main__") and App().main()
