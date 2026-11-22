"""
zork_parser.py
==============
Infocom-style sentence parser for the monad sedenion engine.

Philosophy: the Infocom parser fit in 512KB because it constrained the
problem beautifully. Vocabulary first. Verb governs. Grammar is a table.
Unknown words fail loudly and helpfully. Scope limits candidates.

The Zork parser maps directly to the sedenion operator architecture:

    VERB  → sedenion operator (e₀–e₁₅)
    NOUN  → word in monad vocab (the object being operated on)
    PREP  → A-matrix relation (the connection between objects)
    IT/THEM → anaphor (e₁₁ dereference — last mentioned noun)

This layer sits BETWEEN raw user input and monad.generate().
It gives the engine a verb-governed interface.

Incarnations studied:
    ZIP (Z-machine Interpreter Program), 1979 — MDL Dungeon
    ZIL (Zork Implementation Language), 1981 — Zork 1-3
    ZILCH, 1982-85 — Deadline, Hitchhiker, Trinity
    Inform 6 library (parser.h), 1993 — open source rewrite
    Inform 7, 2006 — natural language rules (too complex, skip)

What we keep:
    1. Verb-first lookup — verb governs the parse
    2. Grammar templates — VERB, VERB NOUN, VERB NOUN PREP NOUN
    3. Pronoun resolution — IT/THEM → last noun
    4. Conjunction splitting — AND chains → multiple actions
    5. Direction shortcuts — N/S/E/W/U/D → move operator
    6. Disambiguation by J_ambient — raise threshold to narrow candidates

What we skip:
    - Object scope (Infocom: "you can't take what you can't see")
      monad uses J_ambient instead — same concept, different dial
    - Multi-object ALL — too complex for now
    - Save/restore/undo — monad handles via bin files

Author: O Captain My Captain
Version: 0.100
"""

import re
from typing import Dict, List, Optional, Tuple, Any


# ── The 16 sedenion operators with their ZIL-style verb lists ─────────────────
# Each operator has a set of natural language verbs that trigger it.
# The verb IS the operator. Zork knew this. The verb is the action.

OPERATOR_VERBS: Dict[int, List[str]] = {
    0:  # identity — examine, look, what, status
        ['look', 'examine', 'x', 'l', 'what', 'describe', 'inspect', 'read',
         'check', 'glance', 'observe', 'study', 'survey', 'scan'],
    1:  # negate — drop, remove, throw, destroy
        ['drop', 'remove', 'throw', 'discard', 'toss', 'destroy', 'break',
         'smash', 'kill', 'attack', 'hit', 'strike', 'fight', 'negate'],
    2:  # bind — put, attach, connect, combine
        ['put', 'place', 'set', 'attach', 'connect', 'bind', 'tie', 'fasten',
         'insert', 'load', 'fill', 'combine', 'merge', 'link', 'join'],
    3:  # name — call, label, title, define
        ['call', 'name', 'label', 'title', 'define', 'say', 'tell',
         'speak', 'shout', 'whisper', 'ask', 'answer', 'reply', 'yell'],
    4:  # apply — use, press, push, activate
        ['use', 'press', 'push', 'activate', 'apply', 'turn', 'pull',
         'flip', 'switch', 'touch', 'feel', 'rub', 'wave', 'operate'],
    5:  # abstract — take, get, pick, lift
        ['take', 'get', 'pick', 'lift', 'grab', 'hold', 'carry',
         'collect', 'gather', 'obtain', 'acquire', 'steal', 'snatch'],
    6:  # branch — go, move, walk, run
        ['go', 'move', 'walk', 'run', 'travel', 'enter', 'exit', 'leave',
         'climb', 'jump', 'fly', 'swim', 'crawl', 'proceed', 'head'],
    7:  # iterate — count, list, search, find
        ['count', 'list', 'search', 'find', 'seek', 'look for', 'scan',
         'iterate', 'enumerate', 'repeat', 'try', 'attempt', 'explore'],
    8:  # recurse — open, unlock, solve, crack
        ['open', 'unlock', 'solve', 'crack', 'decode', 'decipher',
         'unlock', 'unwrap', 'unzip', 'recurse', 'dig', 'cut', 'break open'],
    9:  # allocate — make, create, build, forge
        ['make', 'create', 'build', 'forge', 'construct', 'craft',
         'write', 'draw', 'compose', 'allocate', 'new', 'spawn', 'generate'],
    10: # query — ask, question, wonder, think
        ['ask', 'question', 'wonder', 'think', 'query', 'why', 'how',
         'ponder', 'consider', 'contemplate', 'guess', 'know', 'understand'],
    11: # dereference — follow, point, refer, track
        ['follow', 'point', 'refer', 'track', 'trace', 'pursue',
         'it', 'them', 'that', 'this', 'these', 'those', 'dereference'],
    12: # compose — write, record, note, document
        ['write', 'record', 'note', 'document', 'compose', 'type',
         'transcribe', 'copy', 'print', 'log', 'save', 'capture'],
    13: # parallelize — with, both, all, together
        ['with', 'together', 'simultaneously', 'also', 'and also',
         'parallelize', 'multi', 'both', 'dual', 'split', 'fork'],
    14: # interrupt — stop, quit, pause, break
        ['stop', 'quit', 'pause', 'break', 'cancel', 'abort', 'halt',
         'interrupt', 'end', 'finish', 'done', 'wait', 'z', 'again', 'g'],
    15: # emit — show, print, display, output
        ['show', 'print', 'display', 'output', 'reveal', 'emit',
         'present', 'give', 'offer', 'share', 'send', 'pass'],
}

# Reverse map: word → operator
VERB_TO_OP: Dict[str, int] = {}
for op_k, verbs in OPERATOR_VERBS.items():
    for v in verbs:
        VERB_TO_OP[v] = op_k

# Operator names (for display)
OP_NAMES = {
    0:'identity', 1:'negate', 2:'bind', 3:'name', 4:'apply',
    5:'abstract', 6:'branch', 7:'iterate', 8:'recurse', 9:'allocate',
    10:'query', 11:'dereference', 12:'compose', 13:'parallelize',
    14:'interrupt', 15:'emit',
}

# ── Direction table (Zork shorthand) ─────────────────────────────────────────
DIRECTIONS = {
    'n': 'north', 's': 'south', 'e': 'east', 'w': 'west',
    'u': 'up',    'd': 'down',  'ne': 'northeast', 'nw': 'northwest',
    'se': 'southeast', 'sw': 'southwest',
    'north': 'north', 'south': 'south', 'east': 'east', 'west': 'west',
    'up': 'up', 'down': 'down', 'in': 'in', 'out': 'out',
}

# ── Prepositions (Zork: "put X IN Y", "take X FROM Y") ───────────────────────
PREPS = frozenset([
    'in', 'into', 'inside', 'on', 'onto', 'upon', 'under', 'beneath',
    'behind', 'through', 'from', 'off', 'about', 'with', 'to', 'at',
    'over', 'across', 'against', 'around', 'near', 'beside',
])

# ── Articles and determiners (skipped in parsing, like Zork) ─────────────────
ARTICLES = frozenset(['the', 'a', 'an', 'some', 'any'])

# ── Grammar templates (Infocom pattern table) ─────────────────────────────────
# Each template is a tuple of required slot types.
# VERB is implicit (always first). Templates describe the REST of the input.
#
#   'N'   = noun/object
#   'P'   = preposition
#   'D'   = direction
#   '?'   = optional noun
#
TEMPLATES = [
    (),           # VERB alone         → intransitive   (look, wait, quit)
    ('N',),       # VERB NOUN          → transitive      (take lamp)
    ('N', 'P', 'N'),  # VERB N PREP N → ditransitive    (put lamp in box)
    ('P', 'N'),   # VERB PREP NOUN     → prep-first      (go to tower)
    ('D',),       # direction shorthand → VERB=go + DIR  (n, s, northeast)
]


# ── ParseResult ───────────────────────────────────────────────────────────────

class ParseResult:
    """Result of parsing one sentence."""
    def __init__(self,
                 operator: int,
                 op_name: str,
                 verb_word: str,
                 nouns: List[str],
                 prep: Optional[str],
                 raw: str,
                 error: Optional[str] = None):
        self.operator  = operator    # sedenion dimension 0-15
        self.op_name   = op_name     # human name
        self.verb_word = verb_word   # exact verb token used
        self.nouns     = nouns       # list of noun tokens
        self.prep      = prep        # preposition (or None)
        self.raw       = raw         # original input
        self.error     = error       # parse error (or None)
        self.ok        = error is None

    def __repr__(self):
        if not self.ok:
            return f'ParseResult(ERROR: {self.error})'
        ns = ', '.join(self.nouns) if self.nouns else '—'
        p  = f' {self.prep}' if self.prep else ''
        return f'ParseResult(e{self.operator}={self.op_name}, verb={self.verb_word!r}, nouns=[{ns}]{p})'

    def to_monad_prompt(self) -> str:
        """Convert to a natural language string suitable for monad.generate()."""
        parts = [self.op_name]
        if self.nouns:
            parts.extend(self.nouns[:2])
        if self.prep and len(self.nouns) > 1:
            parts.insert(2, self.prep)
        return ' '.join(parts)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'ok'       : self.ok,
            'operator' : self.operator,
            'op_name'  : self.op_name,
            'verb'     : self.verb_word,
            'nouns'    : self.nouns,
            'prep'     : self.prep,
            'raw'      : self.raw,
            'error'    : self.error,
            'prompt'   : self.to_monad_prompt() if self.ok else None,
        }


# ── ZorkParser ────────────────────────────────────────────────────────────────

class ZorkParser:
    """
    Infocom-style sentence parser for the monad engine.

    Usage:
        parser = ZorkParser()
        result = parser.parse("put the brass lantern in the mailbox")
        # result.operator == 2 (bind)
        # result.nouns    == ['brass lantern', 'mailbox']
        # result.prep     == 'in'

    The parser tracks the last noun for pronoun resolution (IT/THEM),
    mimicking Zork's anaphor mechanism (mapped to monad's e₁₁ dereference).
    """

    def __init__(self, extra_verbs: Optional[Dict[str, int]] = None):
        """
        :param extra_verbs: User-defined verb → operator overrides.
        """
        self._verb_map = dict(VERB_TO_OP)
        if extra_verbs:
            self._verb_map.update(extra_verbs)
        self._last_noun: Optional[str] = None    # pronoun resolution (e₁₁)
        self._last_result: Optional[ParseResult] = None

    # ── Public API ────────────────────────────────────────────────────────────

    def parse(self, text: str) -> ParseResult:
        """
        Parse a natural language sentence into a ParseResult.

        :param text: Raw user input string.
        :returns: ParseResult with operator, nouns, prep (or error).
        """
        text = text.strip()
        if not text:
            return self._err(text, 'Empty input.')

        # Conjunction splitting: "TAKE LAMP AND DROP SWORD" → two actions
        # Return only the first for now; caller handles the rest.
        sentences = self._split_conjunctions(text)
        if len(sentences) > 1:
            # Parse first, stash rest for caller via .remainder
            result = self._parse_one(sentences[0])
            result._remainder = sentences[1:]
            return result
        return self._parse_one(text)

    def parse_all(self, text: str) -> List[ParseResult]:
        """Parse all conjunction-separated sentences."""
        sentences = self._split_conjunctions(text)
        results = []
        for s in sentences:
            r = self._parse_one(s)
            results.append(r)
        return results

    def add_verb(self, word: str, operator: int):
        """Register a custom verb mapping."""
        self._verb_map[word.lower()] = operator

    def last_noun(self) -> Optional[str]:
        """The most recently parsed noun (pronoun resolution target)."""
        return self._last_noun

    # ── Private ───────────────────────────────────────────────────────────────

    def _parse_one(self, text: str) -> ParseResult:
        tokens = self._tokenize(text)
        if not tokens:
            return self._err(text, 'I beg your pardon?')

        # 1. Direction shorthand (N/S/E/W/etc.)
        if tokens[0] in DIRECTIONS:
            direction = DIRECTIONS[tokens[0]]
            self._last_noun = direction
            return ParseResult(6, 'branch', tokens[0], [direction], None, text)

        # 2. Find the verb (always the first token)
        verb_token = tokens[0]

        # Multi-word verbs: "look for", "break open"
        verb_op = None
        verb_used = verb_token
        if len(tokens) >= 2:
            two_word = f'{tokens[0]} {tokens[1]}'
            if two_word in self._verb_map:
                verb_op = self._verb_map[two_word]
                verb_used = two_word
                tokens = [two_word] + tokens[2:]

        if verb_op is None:
            if verb_token in self._verb_map:
                verb_op = self._verb_map[verb_token]
            else:
                # Unknown verb: give helpful error like Infocom
                return self._err(text,
                    f"I don't know the word '{verb_token}'. "
                    f"Try: look, take, put, go, use, open, say, give, find, make, ask")

        rest = tokens[1:]

        # 3. Strip articles
        rest = [t for t in rest if t not in ARTICLES]

        # 4. Pronoun resolution (IT/THEM → last noun)
        rest = [self._last_noun if t in ('it','them','that','this','those','these')
                and self._last_noun else t for t in rest]

        # 5. Split on preposition
        prep, nouns = self._split_prep(rest)

        # 6. Update last noun tracker
        if nouns:
            self._last_noun = nouns[0]

        result = ParseResult(
            operator  = verb_op,
            op_name   = OP_NAMES[verb_op],
            verb_word = verb_used,
            nouns     = nouns,
            prep      = prep,
            raw       = text,
        )
        self._last_result = result
        return result

    def _tokenize(self, text: str) -> List[str]:
        """
        Zork-style tokenizer:
        - lowercase
        - split on whitespace and punctuation
        - 6-letter abbreviation matching for VERBS ONLY (EXAMIN → examine)
        - strip empty tokens
        """
        text = text.lower().strip()
        tokens = re.split(r'[\s,;.!?]+', text)
        tokens = [t.strip() for t in tokens if t.strip()]
        if not tokens:
            return tokens

        # Only expand the first token (the verb) via 6-letter prefix
        first = tokens[0]
        if first not in self._verb_map and first not in DIRECTIONS:
            match = self._expand_prefix(first)
            if match:
                tokens[0] = match

        return tokens

    def _expand_prefix(self, prefix: str) -> Optional[str]:
        """Expand a 6-letter prefix to a known verb (Zork's truncation rule)."""
        if len(prefix) < 4:
            return None
        for word in self._verb_map:
            if word.startswith(prefix) or prefix.startswith(word[:6]):
                return word
        return None

    def _split_prep(self, tokens: List[str]) -> Tuple[Optional[str], List[str]]:
        """
        Split token list into (preposition, [noun_phrases]).
        "brass lantern in the mailbox" → ('in', ['brass lantern', 'mailbox'])
        """
        if not tokens:
            return None, []

        # Find preposition in middle position
        for i, t in enumerate(tokens):
            if t in PREPS and i > 0:
                first  = ' '.join(tokens[:i]).strip()
                second = ' '.join(tokens[i+1:]).strip()
                nouns = [n for n in [first, second] if n]
                return t, nouns

        # No preposition: everything is one noun
        return None, [' '.join(tokens)]

    def _split_conjunctions(self, text: str) -> List[str]:
        """
        Split on conjunctions: "TAKE LAMP AND DROP SWORD" → two sentences.
        Only splits where the second part begins with a known verb.
        "TAKE LAMP AND SWORD" stays as one sentence (no verb in second part).
        """
        parts = re.split(r'\s+and\s+', text, flags=re.IGNORECASE)
        if len(parts) <= 1:
            return [text]

        valid = [parts[0].strip()]
        for p in parts[1:]:
            p = p.strip()
            if not p:
                continue
            first_tok = p.split()[0].lower() if p.split() else ''
            # Second part must start with a known verb to be a new sentence
            if first_tok in self._verb_map or first_tok in DIRECTIONS:
                valid.append(p)
            else:
                # "AND SWORD" — append to the previous sentence's noun
                valid[-1] = valid[-1] + ' and ' + p
        return valid

    def _err(self, raw: str, msg: str) -> ParseResult:
        return ParseResult(0, 'identity', '', [], None, raw, error=msg)

    # ── Pretty diagnostics ────────────────────────────────────────────────────

    def vocabulary(self) -> Dict[str, List[str]]:
        """Return operator→verb_list mapping for inspection."""
        result = {}
        for op in range(16):
            result[OP_NAMES[op]] = OPERATOR_VERBS.get(op, [])
        return result

    def explain(self, result: ParseResult) -> str:
        """Infocom-style parse explanation (debugging/paper demo)."""
        if not result.ok:
            return f"PARSE ERROR: {result.error}"
        lines = [
            f"Verb:      '{result.verb_word}' → e{result.operator} ({result.op_name})",
            f"Objects:   {result.nouns or ['(none)']}",
            f"Prep:      {result.prep or '(none)'}",
            f"monad:     '{result.to_monad_prompt()}'",
            f"Last noun: {self._last_noun or '(none)'}",
        ]
        return '\n'.join(lines)


# ── Envelope Overload: User-defined surface ────────────────────────────────────

class MonadInterface:
    """
    The NS-in-language layer.

    Classical NS: free surface at the fluid-air boundary.
    Language monad: NO free surface. Infinite medium.
    But we need output. The ZorkParser creates an ARTIFICIAL SURFACE.

    J_ambient = the depth of the artificial surface.
    Words lighter than J_ambient float up → output.
    Words heavier sink → dark current (hide in A-matrix, beta, age).

    DIVERGENCE IS OBSERVATION:
        When a word is selected and output, the field extracts it.
        This IS a divergence event: ∇·u = delta(x_word) at that location.
        But NS requires ∇·u = 0 globally. So the extracted information
        must reappear as a source elsewhere.
        It does: the A-matrix edges update (new connections learned),
        beta increments, age adjusts. The total information is conserved.
        Observation = local divergence + equal and opposite A-matrix convergence.
        The information hides in the math. Every observation creates a memory.

    The user-defined envelope:
        J_ambient can be set per-session, per-turn, per-domain.
        High J_ambient: deep surface, few words emerge, compressed output.
        Low J_ambient: shallow surface, more words emerge, creative output.
        Default: OMEGA_ZS = 0.5671432904097838 (the BAO attractor — neutral buoyancy).
    """

    def __init__(self, engine=None, J_ambient: float = 0.5671432904097838):
        """
        :param engine: monad Engine instance (or None for parser-only mode).
        :param J_ambient: Depth of artificial output surface.
        """
        self.parser    = ZorkParser()
        self.engine    = engine
        self.J_ambient = J_ambient
        self._history: List[Tuple[str, ParseResult]] = []

    def set_surface(self, depth: float):
        """Set the J_ambient surface depth. Envelope overload."""
        self.J_ambient = max(0.0, min(1.0, depth))
        if self.engine is not None:
            self.engine._J_ambient = self.J_ambient

    def process(self, user_input: str) -> Dict[str, Any]:
        """
        Parse input → feed to monad → return structured response.

        The NS layer:
            Input sentence  = the velocity field impulse (external forcing)
            ZorkParser      = the boundary condition at the artificial surface
            monad.generate  = the NS time-step (field evolution)
            Output words    = the surface flux (divergence = observation)
            A-matrix update = the source term that balances the observation
        """
        results = self.parser.parse_all(user_input)
        outputs = []

        for r in results:
            entry = {'parse': r.to_dict(), 'response': None, 'noether': None}

            if r.ok and self.engine is not None:
                prompt = r.to_monad_prompt()
                try:
                    gen = self.engine.generate(
                        prompt,
                        n_words=12,
                        learn_prompt=True,
                        J_ambient=self.J_ambient,
                    )
                    entry['response'] = gen.get('response', '')
                    entry['noether']  = gen.get('noether_violation', None)
                    entry['bao']      = gen.get('bao', None)
                except Exception as e:
                    entry['error'] = str(e)

            self._history.append((user_input, r))
            outputs.append(entry)

        return {
            'input'       : user_input,
            'n_sentences' : len(results),
            'outputs'     : outputs,
            'J_ambient'   : self.J_ambient,
        }


# ── CLI demo ───────────────────────────────────────────────────────────────────

def _demo():
    """Interactive Zork-style parser demo without monad engine."""
    parser = ZorkParser()

    TEST_INPUTS = [
        "look",
        "take the brass lantern",
        "put the lamp in the mailbox",
        "go north",
        "n",
        "open the trap door with the key",
        "take lamp and sword",
        "examine it",
        "drop the sword",
        "what is the fibonacci sequence",
        "make a new connection",
        "ask about the riemann hypothesis",
        "parallelize with the sedenion engine",
        "EXAMIN LANTER",          # 6-letter truncation test
        "kill the troll with the sword",
        "unknown verb the thing",
    ]

    print("="*60)
    print("ZORK-STYLE PARSER — monad sedenion interface")
    print(f"Vocabulary: {len(VERB_TO_OP)} verbs, {len(OPERATOR_VERBS)} operators")
    print("="*60)
    print()

    for inp in TEST_INPUTS:
        results = parser.parse_all(inp)
        print(f">>> {inp}")
        for r in results:
            if r.ok:
                print(f"    {r}")
                print(f"    monad prompt: '{r.to_monad_prompt()}'")
            else:
                print(f"    ERROR: {r.error}")
        print()


if __name__ == '__main__':
    _demo()
