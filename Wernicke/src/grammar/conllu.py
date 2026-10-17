"""CoNLL-U reader — the smallest thing that yields sentences as dependency rings."""
from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Iterator, List

_DS = os.path.join(os.path.dirname(__file__), "..", "..", "datasets")
EWT = {n: os.path.join(_DS, "UD_English-EWT", f"en_ewt-ud-{n}.conllu")
       for n in ("train", "dev", "test")}
GUM = {n: os.path.join(_DS, "UD_English-GUM", f"en_gum-ud-{n}.conllu")
       for n in ("train", "dev", "test")}


@dataclass
class Tok:
    id: int; form: str; lemma: str; upos: str; xpos: str; head: int; deprel: str


@dataclass
class Sent:
    text: str
    toks: List[Tok]

    @property
    def root(self) -> Tok | None:
        for t in self.toks:
            if t.head == 0 and t.deprel == "root":
                return t
        return None

    def children(self, tid: int) -> List[Tok]:
        return [t for t in self.toks if t.head == tid]


def read(path: str) -> Iterator[Sent]:
    text, toks = "", []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("# text = "):
                text = line[9:]
            elif not line:
                if toks:
                    yield Sent(text, toks)
                text, toks = "", []
            elif line and not line.startswith("#"):
                c = line.split("\t")
                if "-" in c[0] or "." in c[0]:      # skip MWT / empty nodes
                    continue
                try:
                    toks.append(Tok(int(c[0]), c[1], c[2], c[3], c[4],
                                    int(c[6]) if c[6] != "_" else 0, c[7].split(":")[0]))
                except (ValueError, IndexError):
                    continue
    if toks:
        yield Sent(text, toks)


if __name__ == "__main__":
    n = 0
    for s in read(EWT["dev"]):
        n += 1
        if n <= 3:
            r = s.root
            print(f"\n{s.text}")
            print(f"  root: {r.form}/{r.upos}   deprels off root:",
                  [t.deprel for t in s.children(r.id)])
    print(f"\n{n} sentences in EWT dev")
