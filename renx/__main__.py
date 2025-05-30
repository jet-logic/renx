import unicodedata, re
from os import rename
from os.path import dirname, join
from os.path import splitext
from .findskel import FindSkel
from . import __version__


def asciify(text: str):
    """
    Converts a Unicode string to its closest ASCII equivalent by removing
    accent marks and other non-ASCII characters.
    """
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


def slugify(value: str):
    value = str(value)
    value = asciify(value)
    value = re.sub(r"[^a-zA-Z0-9_.+-]+", "_", value)
    return value


def clean(value: str):
    value = str(value)
    value = re.sub(r"\-+", "-", value).strip("-")
    value = re.sub(r"_+", "_", value).strip("_")
    return value


def urlsafe(name: str, parent=None):
    s = slugify(name)
    if s != name or re.search(r"[_-]\.", s) or re.search(r"[_-]+", s):
        assert slugify(s) == s
        stem, ext = splitext(s)
        return clean(stem) + ext
    return name


sepa_set = r"""!"#$%&'*+,-./:;<=>?@\^_`|~"""
trans_map = {
    "upper": lambda s: s.upper(),
    "lower": lambda s: s.lower(),
    "title": lambda s: s.title(),
    "swapcase": lambda s: s.swapcase(),
    "expandtabs": lambda s: s.expandtabs(),
    "casefold": lambda s: s.casefold(),
    "capitalize": lambda s: s.capitalize(),
    "asciify": asciify,
    "slugify": slugify,
    "urlsafe": urlsafe,
}


def chain_trans(extra: "dict[str, object]", t):
    f = extra.get("transform")
    if f:
        extra["transform"] = lambda s: t(f(s))
    else:
        extra["transform"] = t


def split_subs(s: str):
    extra: "dict[str, object]" = {}
    if not s:
        raise SyntaxError("Empty")
    elif re.match(r"^[\w:]+$", s):
        for x in s.split(":"):
            if x in ["ext", "stem"]:
                extra["which"] = x
            elif x in trans_map.keys():
                chain_trans(extra, trans_map[x])
            else:
                raise SyntaxError(f"Invalid flag {x!r}")
        return ".+", "", extra
    sep = s[0]
    if sep not in sepa_set:
        raise SyntaxError("Separator must be {!r}")
    a = s.split(sep, 3)
    if len(a) > 2:
        search, replace, tail = a[1], a[2], a[3]
        if not search:
            raise SyntaxError(f"Empty search pattern {s!r}")
        if tail:
            flags = None
            for x in tail.split(":"):
                if x in ["ext", "stem"]:
                    extra["which"] = x
                elif x in trans_map.keys():
                    chain_trans(extra, trans_map[x])
                else:
                    try:
                        re.compile(rf"(?{x})")
                    except Exception as e:
                        raise SyntaxError(f"Invalid flag {x!r}: {e}")
                    flags = x
            if flags:
                search = f"(?{flags}){search}"
        return search, replace, extra
    raise SyntaxError(f"Invalid pattern  {s!r}")


class App(FindSkel):
    def __init__(self) -> None:
        super().__init__()
        self.dry_run = True
        self.depth_first = True
        self._glob_excludes = []
        self._glob_includes = []
        self._dir_depth = ()
        self._file_sizes = []
        self._paths_from = []

    def add_arguments(self, argp):

        argp.add_argument("--subs", "-s", action="append", default=[], help="subs regex")
        argp.add_argument("--lower", action="store_true", help="to lower case")
        argp.add_argument("--upper", action="store_true", help="to upper case")
        argp.add_argument("--urlsafe", action="store_true", help="only urlsafe characters")
        argp.add_argument("--version", action="version", version=f"{__version__}")
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

        def _append(rex, rep: str, extra: "dict[str:object]"):
            if extra:

                def fn(name: str, parent):
                    x = extra.get("which", "")
                    if x == "stem":
                        S, x = splitext(name)
                        fin = lambda r: r + x
                    elif x == "ext":
                        x, S = splitext(name)
                        fin = lambda r: x + r
                    else:
                        assert x == ""
                        S = name
                        fin = lambda r: r
                    f = extra.get("transform")
                    if f:
                        R = lambda m: f(m.group(0))
                    else:
                        R = rep

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
        self._walk_paths()

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


def main():
    """CLI entry point."""
    App().main()


if __name__ == "__main__":
    main()
