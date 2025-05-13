import unicodedata, re
from os import rename
from os.path import dirname, join
from os.path import splitext
from .scantree import ScanTree


def asciify(text: str):
    """
    Converts a Unicode string to its closest ASCII equivalent by removing
    accent marks and other non-ASCII characters.
    """
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


def slugify(value):
    value = str(value)
    value = asciify(value)
    value = re.sub(r"[^a-zA-Z0-9_.+-]+", "_", value)
    return value


def clean(value):
    value = str(value)
    value = re.sub(r"\-+", "-", value).strip("-")
    value = re.sub(r"_+", "_", value).strip("_")
    return value


def urlsafe(name, parent=None):
    s = slugify(name)
    if s != name or re.search(r"[_-]\.", s) or re.search(r"[_-]+", s):
        assert slugify(s) == s
        stem, ext = splitext(s)
        return clean(stem) + ext
    return name


def split_subs(s: str):
    a = s[1:].split(s[0], 3)
    if len(a) > 1:
        search = a[0]
        replace = a[1]
        extra = {}
        if not search:
            raise RuntimeError(f"Empty search pattern {s!r}")
        if len(a) > 2:
            flags = None
            for x in a[2:]:
                if x in [
                    "upper",
                    "lower",
                    "title",
                    "swapcase",
                    "expandtabs",
                    "casefold",
                    "capitalize",
                    "asciify",
                    "slugify",
                    "urlsafe",
                    "ext",
                    "stem",
                ]:
                    if x not in ["ext", "stem"]:
                        assert not replace
                        pass
                    extra[x] = True
                else:
                    flags = x
            if flags:
                search = f"(?{flags}){search}"
        return search, replace, extra
    raise RuntimeError(f"Invalid pattern  {s!r}")


class App(ScanTree):
    def __init__(self) -> None:
        self._entry_filters = []
        super().__init__()

    def add_arguments(self, argp):
        self.dry_run = True
        self.bottom_up = True
        self.excludes = []
        self.includes = []
        argp.add_argument("--subs", "-s", action="append", default=[], help="subs regex")
        argp.add_argument("--lower", action="store_true", help="to lower case")
        argp.add_argument("--upper", action="store_true", help="to upper case")
        argp.add_argument("--urlsafe", action="store_true", help="only urlsafe characters")
        if not argp.description:
            argp.description = "Renames files matching re substitution pattern"

        super(App, self).add_arguments(argp)

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
            _subs.append(urlsafe)

        def _append(rex, rep: str, extra):
            if extra:

                def fn(name: str, parent):
                    if extra.get("stem"):
                        S, x = splitext(name)
                        fin = lambda r: r + x
                    elif extra.get("ext"):
                        x, S = splitext(name)
                        fin = lambda r: x + r
                    else:
                        S = name
                        fin = lambda r: r

                    # def fr():
                    #     return rex.sub(rep, S)

                    if extra.get("lower"):
                        R = lambda m: m.group(0).lower()
                    elif extra.get("upper"):
                        R = lambda m: m.group(0).upper()
                    elif extra.get("title"):
                        R = lambda m: m.group(0).title()
                    elif extra.get("swapcase"):
                        R = lambda m: m.group(0).swapcase()
                    elif extra.get("casefold"):
                        R = lambda m: m.group(0).casefold()
                    elif extra.get("capitalize"):
                        R = lambda m: m.group(0).capitalize()
                    elif extra.get("asciify"):
                        R = lambda m: asciify(m.group(0))
                    elif extra.get("urlsafe"):
                        R = lambda m: urlsafe(m.group(0))
                    elif extra.get("slugify"):
                        R = lambda m: urlsafe(m.group(0))
                    else:
                        R = rep
                    # return fin(fx(fr()))

                    return fin(rex.sub(R, S))

            else:

                def fn(name, parent):
                    return rex.sub(rep, name)

            fn.regx = rex

            # print("REX", rex, rep)
            _subs.append(fn)

        for s in self.subs:
            search, replace, extra = split_subs(s)
            try:
                rex = regex(search)
            except Exception as e:
                raise RuntimeError(f"Bad regexp {search!r}: {e}")
            _append(rex, replace, extra)

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
            # print("fn", getattr(fn, "regx", "?"))
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
