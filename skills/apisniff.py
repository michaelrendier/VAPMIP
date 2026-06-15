"""
skills/apisniff.py — Code introspection and sedenion address mapping for Ptolemy.

:description:
    APISniff reads Ptolemy's own codebase and all imported modules via
    dir() + inspect, maps every callable to a sedenion coordinate via
    cam_encode(name + signature + docstring + source), and builds
    monad_sedenion.bin — the sedenion field's self-knowledge of code.

    Three layers:
      Layer 1 — Python: dir() + inspect on all skills + stdlib
      Layer 2 — C binary: PtolC function signatures + ctypes numeric addresses
      Layer 3 — Sedenion algebra: all 256 multiplication table entries in prose

    The multiplication table is the Rosetta Stone:
      "e3 multiplied by e4 gives e7 with positive sign —
       name times apply gives iterate — naming a function and applying it
       creates iteration."
    Ptolemy reading this learns to navigate his own instruction set.

    monad_sedenion.bin is NOT a speaking bin. It is a code-knowledge bin.
    Load it alongside monad.bin to give Ptolemy awareness of his own structure:
      query("urllib")   → high beta → Ptolemy knows urllib's neighborhood
      generate("fetch") → words cluster near e9_allocate + e11_dereference

:classes:
    APISniff
    SedenionAddressBook
"""

import os
import sys
import math
import inspect
import importlib
import threading
import pickle
from pathlib import Path
from typing import Optional

# ── Sedenion constants (mirrors monad.py) ─────────────────────────────────────
OMEGA_ZS   = 0.5671432904097838
GAP        = 0.000707
SIGMA_CRIT = 0.5
PHI        = (1.0 + math.sqrt(5.0)) / 2.0

_OP = {
    0:  'identity',    1:  'negate',      2:  'bind',        3:  'name',
    4:  'apply',       5:  'abstract',    6:  'branch',      7:  'iterate',
    8:  'recurse',     9:  'allocate',    10: 'query',       11: 'dereference',
    12: 'compose',     13: 'parallelize', 14: 'interrupt',   15: 'emit',
}

# Standard library modules Ptolemy uses — sniff these for code addresses
_STDLIB_TARGETS = [
    'urllib.request', 'urllib.parse', 'urllib.robotparser', 'urllib.error',
    'json', 'os', 'os.path', 'sys', 'math', 'threading', 'socket',
    'time', 'pathlib', 'collections', 'hashlib', 'pickle', 'struct',
    'configparser', 'inspect', 'importlib', 'shutil', 're', 'xml.etree.ElementTree',
    'dataclasses', 'typing', 'subprocess',
]

# Ptolemy's own skill modules — all get sniffed
_SKILL_MODULES = [
    'skills.config', 'skills.logger', 'skills.staging', 'skills.monitor',
    'skills.shell', 'skills.search', 'skills.crawler', 'skills.network',
    'skills.scholar', 'skills.lexicon', 'skills.sources', 'skills.draw',
    'skills.apisniff',
]


# ── Code-semantic word sets for _code_encode ─────────────────────────────────
# Each set directly maps to a sedenion dimension.
# Words here are CODE tokens — parts of names, signatures, docstrings.

_CE_NEGATE    = {'not','no','none','null','false','del','remove','delete',
                 'clear','close','stop','cancel','abort','reset','drop','kill'}
_CE_BIND      = {'bind','connect','link','join','attach','add','set','register',
                 'subscribe','hook','assign','put','insert','attach','glue','merge'}
_CE_NAME      = {'name','label','id','key','tag','mark','identify',
                 'format','str','repr','hash','symbol','token',
                 'alias','rename','qualify','stringify','describe',
                 'word','text','definition','meaning','concept','term',
                 'english','language','vocabulary','lexicon','syntax'}
_CE_APPLY     = {'call','invoke','apply','execute','run','eval','dispatch','fire',
                 'trigger','process','perform','do','handle','compute','calc'}
_CE_ABSTRACT  = {'type','class','abstract','base','interface','generic','template',
                 'schema','model','meta','pattern','spec','proto','kind','sort',
                 'group','categorize','classify','typeof','isinstance'}
_CE_BRANCH    = {'if','check','test','verify','validate','assert','filter',
                 'match','select','choose','compare','equals','when','guard',
                 'allow','deny','permit','reject','condition'}
_CE_ITERATE   = {'iter','each','all','map','scan','walk','enumerate','loop',
                 'repeat','next','list','stream','range','page','batch','chunk',
                 'crawl','traverse','visit','foreach','zip','chain','cycle'}
_CE_RECURSE   = {'recurse','recursive','depth','stack','nested','tree','self',
                 'follow','traverse','descent','fold','unfold','fix','fixpoint'}
_CE_ALLOC     = {'open','read','load','fetch','get','download','request',
                 'receive','acquire','import','include','socket','file','http',
                 'ftp','init','create','new','alloc','make','build','spawn',
                 'pull','retrieve','restore','deserialize','decode','parse',
                 'learn','train','study','teach','ingest','absorb',
                 'disk','store','persist','checkpoint','cache','buffer',
                 'scan','crawl','scrape','harvest',
                 'url','uri','path','resource','address','endpoint'}
_CE_QUERY     = {'search','find','query','lookup','seek','locate','where',
                 'which','what','who','match','scan','grep','index','contains',
                 'exists','has','count','discover','detect',
                 'inspect','introspect','browse','dir','enumerate',
                 'academic','paper','arxiv','pubmed','scholar','doi',
                 'journal','citation','research','study'}
_CE_DEREF     = {'deref','follow','resolve','unpack','unwrap','yield','ref',
                 'indirect','access','index','item','peek','extract','field',
                 'attr','getattr','getitem','pop','head','tail','first','last'}
_CE_COMPOSE   = {'compose','chain','pipe','then','wrap','decorate','combine',
                 'concat','append','extend','reduce','fold','accumulate','and',
                 'sequence','series','before','after','next','then'}
_CE_PARALLEL  = {'thread','async','await','concurrent','parallel','lock',
                 'mutex','semaphore','pool','worker','process','fork','spawn',
                 'event','future','task','schedule','queue','barrier','sync'}
_CE_INTERRUPT = {'error','exception','raise','throw','fail','abort','cancel',
                 'timeout','retry','warn','interrupt','signal','trap','panic',
                 'halt','break','exit','eof','disconnect','reset'}
_CE_EMIT      = {'write','send','emit','print','output','return','publish',
                 'broadcast','flush','dump','export','save','report','log',
                 'render','display','show','respond','reply','post','push',
                 'stream','yield','produce','generate','encode','serialize',
                 'speak','say','utter','express','speak','voice','announce',
                 'draw','plot','diagram','visualize','visualise','sketch',
                 'chart','graph','paint','render','raster','svg','png'}

# Module name → dimension hint (for module-level context)
_MODULE_HINTS = {
    'threading': 13,  'asyncio': 13,  'multiprocessing': 13,
    'socket':    9,   'urllib':  9,   'http':   9,   'ftp':  9,
    'os':        9,   'io':      9,   'pathlib': 9,
    'json':      12,  'xml':     12,  'struct':  12, 'pickle': 12,
    're':        10,  'fnmatch': 10,  'glob':    10,
    'math':      5,   'decimal': 5,   'fractions': 5,
    'hashlib':   3,   'hmac':    3,   'uuid':    3,
    'logging':   15,  'warnings': 14,
    'sys':       0,   'builtins': 0,
    'time':      7,   'datetime': 7,  'calendar': 7,
    'itertools': 7,   'functools': 12,
    'collections': 5, 'typing':   5,   'dataclasses': 5,
    'inspect':   8,   'importlib': 4,
}


def _split_code_token(tok: str) -> list:
    """
    Split a compound code token into semantic atoms.

    Handles: camelCase, snake_case (pre-split), dotted paths (pre-split),
    and prefix stripping ('url' → 'url', 'urlopen' → ['url', 'open']).
    Applied BEFORE the word set lookups in _code_encode.

    :param tok: Lowercase single token (no dots, no underscores).
    :returns: List of sub-tokens.
    :rtype: list
    """
    import re
    # Split CamelCase: httpRequest → http request
    camel = re.sub(r'([a-z])([A-Z])', r'\1 \2', tok).lower()
    parts = camel.split()
    # For short tokens that might be prefix+word, try known 2-4 char prefixes
    expanded = []
    # Only genuine tech abbreviations — not short English prefixes (re/un/de)
    # that falsely split words like request→re+quest, remove→re+move
    _prefixes = ('url', 'http', 'ftp', 'tcp', 'udp', 'api', 'sdk',
                 'sql', 'xml', 'csv', 'gnu', 'ssl', 'tls', 'gui',
                 'uri', 'utf', 'uuid', 'sha', 'md5', 'hmac',
                 'get', 'set', 'has')
    for part in parts:
        matched = False
        for pfx in _prefixes:
            if part.startswith(pfx) and len(part) > len(pfx) + 1:
                expanded.append(pfx)
                expanded.append(part[len(pfx):])
                matched = True
                break
        if not matched:
            expanded.append(part)
    return expanded


# Pre-build reverse lookup: each keyword → dimension, for fast substring scan
_CE_SETS = [
    (1, _CE_NEGATE), (2, _CE_BIND), (3, _CE_NAME), (4, _CE_APPLY),
    (5, _CE_ABSTRACT), (6, _CE_BRANCH), (7, _CE_ITERATE), (8, _CE_RECURSE),
    (9, _CE_ALLOC), (10, _CE_QUERY), (11, _CE_DEREF), (12, _CE_COMPOSE),
    (13, _CE_PARALLEL), (14, _CE_INTERRUPT), (15, _CE_EMIT),
]


def _code_encode(text: str, depth: int = -1) -> list:
    """
    Structural sedenion encoder for code constructs.

    Unlike cam_encode (linguistic encoder for prose), _code_encode activates
    sedenion dimensions based on CODE SEMANTICS: what does this construct DO?

    Two matching passes per token:
      1. Exact match against keyword sets (fast)
      2. Substring match for compound tokens like 'urlopen' → finds 'open' in e9

    e0 (identity/ground) encodes MODULE DEPTH, not "what's left over":
      depth=0 (builtins, primitives)   → e0=1.0  (pure ground state)
      depth=1 (os.remove, math.sqrt)   → e0=0.5
      depth=2 (os.path.join)           → e0=0.33
      depth=3+ (urllib.request.urlopen) → e0→0
    Query strings with no dots → depth=-1 → e0=GAP (no identity boost for queries)

    :param text: Callable name, query string, or mixed prose.
    :param depth: Dot-depth of callable (≥0 for addresses; -1 = query mode, no e0 boost).
    :returns: Unit sedenion (16 floats).
    :rtype: list
    """
    # Tokenise: replace structural separators, then split
    raw_tokens = text.lower().replace('.', ' ').replace('_', ' ').split()

    # Expand compound tokens (camelCase, prefix+word)
    tokens = []
    for rt in raw_tokens:
        tokens.extend(_split_code_token(rt))

    n = max(len(tokens), 1)
    s = [0.0] * 16

    for tok in tokens:
        # Module-level context (exact module name → dimension boost)
        if tok in _MODULE_HINTS:
            s[_MODULE_HINTS[tok]] += 1.0 / n

        # Pass 1: exact keyword match (full token is a known word)
        for dim, kset in _CE_SETS:
            if tok in kset:
                s[dim] += 1.0 / n

        # Pass 2: substring match for LONGER tokens that CONTAIN a keyword
        if len(tok) > 3:
            for dim, kset in _CE_SETS:
                for kw in kset:
                    if len(kw) >= 3 and kw in tok and kw != tok:
                        s[dim] += 0.5 / n  # half weight for substring hit
                        break

    # e0 = ground-state depth signal: shallow/primitive calls have high e0
    # depth -1 (user query) → GAP only — no identity boost for queries
    if depth >= 0:
        s[0] = 1.0 / (depth + 1)

    # Ensure minimum floor (mirrors monad.py GAP)
    s = [max(x, GAP) for x in s]

    # Unit normalize
    mag = sum(x ** 2 for x in s) ** 0.5
    if mag < 1e-12:
        mag = 1.0
    return [x / mag for x in s]


# ── Operator semantic keywords — for corpus_text enrichment ──────────────────
_OP_KEYWORDS = {
    0:  ['identity', 'passthrough', 'unit', 'default', 'noop', 'scalar'],
    1:  ['negate', 'not', 'invert', 'complement', 'reverse', 'opposite'],
    2:  ['bind', 'connect', 'link', 'associate', 'join', 'attach', 'glue'],
    3:  ['name', 'label', 'declare', 'register', 'identify', 'key', 'symbol'],
    4:  ['apply', 'call', 'invoke', 'execute', 'run', 'evaluate', 'dispatch'],
    5:  ['abstract', 'generalize', 'classify', 'type', 'pattern', 'template'],
    6:  ['branch', 'if', 'condition', 'select', 'choose', 'gate', 'switch'],
    7:  ['iterate', 'loop', 'sequence', 'repeat', 'each', 'map', 'enumerate'],
    8:  ['recurse', 'self', 'depth', 'stack', 'recursive', 'fixpoint'],
    9:  ['allocate', 'fetch', 'load', 'open', 'get', 'acquire', 'request',
         'download', 'read', 'receive', 'store', 'save', 'write'],
    10: ['query', 'search', 'find', 'lookup', 'where', 'match', 'filter',
         'seek', 'locate', 'retrieve'],
    11: ['dereference', 'follow', 'resolve', 'unpack', 'access', 'pointer',
         'ref', 'indirect', 'yield'],
    12: ['compose', 'chain', 'pipe', 'then', 'after', 'sequence', 'pipeline'],
    13: ['parallelize', 'concurrent', 'async', 'thread', 'worker', 'pool',
         'simultaneous', 'lock', 'sync'],
    14: ['interrupt', 'signal', 'exception', 'error', 'raise', 'halt',
         'abort', 'cancel', 'timeout', 'close'],
    15: ['emit', 'output', 'return', 'send', 'print', 'write', 'respond',
         'publish', 'yield', 'result'],
}

# Name fragment → operator hints for enrichment
_NAME_HINTS = {
    'open':    [9, 11],    'read':    [9],       'write':   [15, 9],
    'fetch':   [9, 10],   'load':    [9],        'save':    [9, 15],
    'get':     [9, 10],   'set':     [2, 3],     'put':     [9, 15],
    'send':    [15],      'recv':    [9],         'close':   [14],
    'find':    [10],      'search':  [10],        'match':   [10, 6],
    'filter':  [10, 6],   'map':     [7, 4],      'reduce':  [8, 12],
    'encode':  [12, 5],   'decode':  [11, 12],   'parse':   [11, 5],
    'format':  [15, 12],  'print':   [15],        'log':     [15],
    'init':    [9, 2],    'create':  [9, 3],      'delete':  [1, 14],
    'update':  [2, 9],    'insert':  [2, 9],      'remove':  [1, 14],
    'join':    [2, 12],   'split':   [1, 7],      'strip':   [1, 5],
    'sort':    [7, 5],    'iter':    [7],          'next':    [7, 11],
    'call':    [4],       'apply':   [4],          'invoke':  [4],
    'raise':   [14],      'catch':   [6, 14],      'try':     [6, 8],
    'lock':    [13, 2],   'unlock':  [13, 1],      'wait':    [7, 14],
    'query':   [10, 4],   'request': [9, 4],       'respond': [15],
    'sleep':   [14, 7],   'run':     [4, 7],        'start':   [4, 9],
    'stop':    [14, 1],   'hash':    [12, 3],        'check':   [6, 10],
    'name':    [3],       'label':   [3],            'tag':     [3],
    'type':    [5, 3],    'class':   [5],             'meta':    [5, 3],
    'emit':    [15],      'yield':   [11, 15],        'bind':    [2, 3],
    'chain':   [12],      'pipe':    [12],             'wrap':    [12, 5],
    'error':   [14],      'warn':    [14, 15],         'info':    [15, 3],
    'seed':    [9, 2],    'index':   [3, 10],          'report':  [15, 10],
    'learn':   [2, 5],    'ingest':  [9, 2],           'score':   [10, 15],
    'encode':  [12, 5],   'decode':  [11, 12],
}


def _enrich_description(full_name: str, signature: str, doc: str,
                        source_snippet: str) -> str:
    """
    Build a richer cam_encode input by injecting operator-domain keywords.

    Short API names like 'urlopen' give sparse sedenion signal. This function
    adds semantic context words derived from name fragment analysis so that
    cam_encode sees full prose, not just a function stub.

    :param full_name: Dotted callable name.
    :param signature: Inspect signature string.
    :param doc: Docstring (can be empty).
    :param source_snippet: Source code fragment.
    :returns: Enriched description string for cam_encode.
    :rtype: str
    """
    name_lower = full_name.lower().replace('.', ' ').replace('_', ' ')

    # Collect operator hints from name fragments
    hint_ops = set()
    for fragment, ops in _NAME_HINTS.items():
        if fragment in name_lower:
            for op in ops:
                hint_ops.add(op)

    # Gather semantic words for matched operators
    semantic_words = []
    for op in sorted(hint_ops):
        semantic_words.extend(_OP_KEYWORDS.get(op, [])[:3])

    # Module context: the dotted path tells us the domain
    parts = full_name.split('.')
    module_ctx = ' '.join(parts[:-1]) if len(parts) > 1 else ''

    # Compose the full enriched text
    doc_text   = doc[:300].replace('\n', ' ') if doc else ''
    src_text   = source_snippet[:150].replace('\n', ' ') if source_snippet else ''
    sem_text   = ' '.join(semantic_words) if semantic_words else ''

    pieces = [
        full_name, signature, module_ctx,
        doc_text, src_text, sem_text,
    ]
    return ' '.join(p for p in pieces if p.strip())


def _cosine_similarity(a: list, b: list) -> float:
    """
    Cosine similarity between two 16-float sedenion vectors.

    :param a: First sedenion vector.
    :param b: Second sedenion vector.
    :returns: Similarity in [−1, 1]; higher = more similar.
    :rtype: float
    """
    dot  = sum(a[k] * b[k] for k in range(16))
    mag_a = sum(a[k] ** 2 for k in range(16)) ** 0.5
    mag_b = sum(b[k] ** 2 for k in range(16)) ** 0.5
    denom = mag_a * mag_b
    return dot / denom if denom > 1e-12 else 0.0


class SedenionAddressBook:
    """
    Maps code constructs to sedenion coordinates and back.
    Persists as .ptolrc [code_addresses] entries and as monad_sedenion.bin.

    :param engine: Engine instance (for cam_encode access).
    """

    def __init__(self, engine):
        self._engine = engine
        self._book   = {}   # full_name → {'sedenion', 'signature', 'doc', 'dim_role'}
        self._index  = {}   # peak_dim → list of full_names
        self._lock   = threading.Lock()

    def add(self, full_name: str, signature: str, doc: str,
            source_snippet: str = ''):
        """
        Add a callable to the address book.

        Uses _code_encode (structural sedenion encoder for code) rather than
        cam_encode (linguistic encoder). This gives each callable a sedenion
        address that reflects what it DOES (allocate, emit, query…) rather
        than its surface linguistic features.

        :param full_name: Fully qualified name (e.g. 'urllib.request.urlopen').
        :param signature: Callable signature string.
        :param doc: Docstring.
        :param source_snippet: First 300 chars of source.
        """
        # Build the probe text from name + module path + doc words
        doc_words = ' '.join(doc.lower().split()[:40]) if doc else ''
        probe = f"{full_name} {doc_words}"
        depth = full_name.count('.')
        sed  = _code_encode(probe, depth=depth)
        peak = max(range(16), key=lambda k: abs(sed[k]))
        entry = {
            'sedenion':    sed,
            'signature':   signature,
            'doc':         doc[:500],
            'source':      source_snippet[:300],
            'peak_dim':    peak,
            'operator':    _OP.get(peak, 'unknown'),
        }
        with self._lock:
            self._book[full_name] = entry
            if peak not in self._index:
                self._index[peak] = []
            if full_name not in self._index[peak]:
                self._index[peak].append(full_name)

    def nearest(self, sed: list, n: int = 5) -> list:
        """
        Find n closest known callables to a sedenion coordinate.

        Full cosine similarity scan across all stored entries.
        Both the query sed and all stored seds MUST be encoded with the same
        encoder (_code_encode) — do not mix with cam_encode inputs.

        :param sed: Query sedenion from _code_encode (16 floats).
        :param n: Number of results.
        :returns: List of (full_name, similarity, operator) tuples,
                  highest similarity first.
        :rtype: list
        """
        results = []
        with self._lock:
            for name, entry in self._book.items():
                sim = _cosine_similarity(sed, entry['sedenion'])
                results.append((sim, name, entry['operator']))
        results.sort(reverse=True)
        return [(name, sim, op) for sim, name, op in results[:n]]

    def nearest_code(self, query: str, n: int = 5) -> list:
        """
        Find n callables nearest to a code-semantic query string.

        Encodes the query with _code_encode (structural encoder) so that
        'fetch url download' maps to e9_allocate, not e3_name.

        :param query: Human-readable code concept ('fetch url', 'emit output').
        :param n: Number of results.
        :returns: List of (full_name, similarity, operator) tuples.
        :rtype: list
        """
        sed = _code_encode(query)
        return self.nearest(sed, n)

    def operator_cluster(self, op_idx: int) -> list:
        """
        All callables whose peak sedenion dimension is op_idx.
        This IS the sedenion neighborhood for that operator.

        :param op_idx: Sedenion dimension index 0-15.
        :returns: List of (full_name, peak_value) tuples.
        :rtype: list
        """
        results = []
        with self._lock:
            for name, entry in self._book.items():
                if entry['peak_dim'] == op_idx:
                    peak_val = abs(entry['sedenion'][op_idx])
                    results.append((name, peak_val))
        results.sort(key=lambda x: -x[1])
        return results

    def corpus_text(self) -> str:
        """
        Generate ingestion text from address book.

        Each entry becomes a rich prose sentence: name, operator role,
        docstring, and operator-domain keywords. This gives Crank.learn()
        enough signal to build sedenion associations between code concepts.

        :returns: Full corpus text.
        :rtype: str
        """
        lines = []
        with self._lock:
            for name, entry in self._book.items():
                op   = entry['operator']
                sig  = entry['signature']
                doc  = entry['doc'][:120].replace('\n', ' ')
                # Pull semantic words for this operator dimension
                sem  = ' '.join(_OP_KEYWORDS.get(entry['peak_dim'], [])[:4])
                lines.append(
                    f"{name}{sig} is a {op} operation meaning {sem}. {doc}"
                )
        return '\n'.join(lines)

    def save(self, path: str):
        """
        Persist address book to disk.

        :param path: Output path.
        """
        with open(path, 'wb') as fh:
            pickle.dump({'book': self._book, 'index': self._index,
                         'version': 2}, fh)

    def load(self, path: str) -> bool:
        """
        Load address book from disk.

        Handles migration from v1 (string-keyed index) to v2 (int-keyed).

        :param path: Input path.
        :returns: True on success.
        :rtype: bool
        """
        try:
            with open(path, 'rb') as fh:
                data = pickle.load(fh)
            book  = data.get('book',  {})
            index = data.get('index', {})
            version = data.get('version', 1)
            # v1 → v2 migration: rebuild int-keyed index from book
            if version < 2 or (index and not all(isinstance(k, int) for k in index)):
                index = {}
                for name, entry in book.items():
                    peak = entry.get('peak_dim', 0)
                    if peak not in index:
                        index[peak] = []
                    index[peak].append(name)
            with self._lock:
                self._book  = book
                self._index = index
            return True
        except Exception:
            return False


class APISniff:
    """
    Code browser and sedenion address mapper.

    Reads all imported modules via dir() + inspect.
    Maps every callable to a sedenion coordinate.
    Generates algebra corpus (multiplication table in prose).
    Builds monad_sedenion.bin.

    :param engine: Engine instance.
    :param logger: PtolLogger instance (optional).
    """

    def __init__(self, engine, logger=None):
        self._engine  = engine
        self._logger  = logger
        self._book    = SedenionAddressBook(engine)
        self._sed_table = None  # cached from monad

    def _log(self, msg: str):
        if self._logger:
            self._logger.session('apisniff', note=msg)
        else:
            print(f"[apisniff] {msg}", file=sys.stderr)

    # ── Layer 1: Python callables ─────────────────────────────────────────

    def sniff_module(self, module_name: str) -> int:
        """
        Introspect a module by name. Extracts all callables.

        :param module_name: Dotted module name (e.g. 'urllib.request').
        :returns: Number of callables found.
        :rtype: int
        """
        try:
            mod = importlib.import_module(module_name)
        except ImportError:
            return 0
        count = 0
        for attr_name in dir(mod):
            if attr_name.startswith('__'):
                continue
            obj = getattr(mod, attr_name, None)
            if obj is None:
                continue
            if callable(obj) or inspect.isclass(obj):
                full_name = f"{module_name}.{attr_name}"
                self._sniff_callable(full_name, obj)
                count += 1
            # Also sniff class methods one level deep
            if inspect.isclass(obj):
                for method_name in dir(obj):
                    if method_name.startswith('_'):
                        continue
                    method = getattr(obj, method_name, None)
                    if callable(method):
                        mn = f"{module_name}.{attr_name}.{method_name}"
                        self._sniff_callable(mn, method)
                        count += 1
        return count

    def _sniff_callable(self, full_name: str, obj):
        """Extract metadata from a single callable and add to address book."""
        sig = ''
        doc = ''
        src = ''
        try:
            sig = str(inspect.signature(obj))
        except (ValueError, TypeError):
            pass
        try:
            doc = inspect.getdoc(obj) or ''
        except Exception:
            pass
        try:
            raw = inspect.getsource(obj)
            src = raw[:300]
        except (OSError, TypeError):
            pass
        self._book.add(full_name, sig, doc, src)

    def sniff_self(self) -> int:
        """
        Sniff all Ptolemy skill modules.

        :returns: Total callables found.
        :rtype: int
        """
        total = 0
        for mod_name in _SKILL_MODULES:
            n = self.sniff_module(mod_name)
            self._log(f"sniffed {mod_name}: {n} callables")
            total += n
        # Also sniff monad.py directly
        try:
            import monad as _monad
            for attr in dir(_monad):
                if attr.startswith('_'):
                    continue
                obj = getattr(_monad, attr, None)
                if callable(obj) or inspect.isclass(obj):
                    self._sniff_callable(f"monad.{attr}", obj)
                    total += 1
        except ImportError:
            pass
        self._log(f"sniff_self total: {total}")
        return total

    def sniff_stdlib(self) -> int:
        """
        Sniff Python standard library modules Ptolemy uses.

        :returns: Total callables found.
        :rtype: int
        """
        total = 0
        for mod_name in _STDLIB_TARGETS:
            n = self.sniff_module(mod_name)
            if n:
                self._log(f"sniffed stdlib {mod_name}: {n} callables")
            total += n
        return total

    # ── Layer 2: C binary ─────────────────────────────────────────────────

    def sniff_c_source(self, c_path: str) -> int:
        """
        Parse C source file for function signatures.
        Extracts return type + name + parameter list from function definitions.
        Maps each to a sedenion coordinate.

        :param c_path: Path to .c or .h file.
        :returns: Number of functions found.
        :rtype: int
        """
        import re
        try:
            src = open(c_path, encoding='utf-8', errors='ignore').read()
        except OSError:
            return 0

        # Match C function declarations: return_type name(params)
        # Covers monad_*, state_*, daemon_*, tok_*, plog_*, ingest_*,
        # token_*, filetype_*, and any other PtolC naming conventions
        pattern = re.compile(
            r'^(?:(?:static|extern|inline|void|int|double|float|char|'
            r'unsigned|const)\s+)*'
            r'([\w\s\*]+?)\s+'
            r'(monad_\w+|state_\w+|daemon_\w+|tok_\w+|plog_\w+|'
            r'ingest_\w+|token_\w+|filetype_\w+|filter_\w+|'
            r'ptol_\w+|crank_\w+|cam_\w+|sed_\w+|bao_\w+)\s*'
            r'\(([^)]{0,200})\)',
            re.MULTILINE
        )
        count = 0
        for m in pattern.finditer(src):
            ret_type = m.group(1).strip()
            fn_name  = m.group(2).strip()
            params   = m.group(3).strip()
            full_name = f"PtolC.{fn_name}"
            sig  = f"({params}) -> {ret_type}"
            # Extract comment block before function as doc
            start = max(0, m.start() - 300)
            before = src[start:m.start()]
            doc_match = re.search(r'/\*(.*?)\*/', before, re.DOTALL)
            doc = doc_match.group(1).strip() if doc_match else ''
            self._book.add(full_name, sig, doc, '')
            count += 1
        self._log(f"sniffed C source {c_path}: {count} functions")
        return count

    def sniff_c_numeric(self, lib_path: str) -> int:
        """
        Load a compiled .so and map function addresses via ctypes numeric encoding.
        The function pointer (integer address) is encoded via sensor_encode(addr, 'numeric').
        This maps physical memory address → sedenion coordinate.

        :param lib_path: Path to .so shared library.
        :returns: Number of symbols mapped.
        :rtype: int
        """
        try:
            import ctypes
            from monad import sensor_encode
            lib    = ctypes.CDLL(lib_path)
            count  = 0
            # Attempt to find known Ptolemy C exports
            known_fns = [
                'ptol_fire', 'ptol_learn', 'ptol_j_mu', 'ptol_a_propagate',
                'ptol_cam_encode', 'ptol_sed_mul', 'ptol_bao_check',
                'crank_learn', 'crank_emit', 'crank_sigma_candidates',
            ]
            for fn_name in known_fns:
                try:
                    fn_ptr = getattr(lib, fn_name)
                    addr   = ctypes.cast(fn_ptr, ctypes.c_void_p).value or 0
                    sed    = sensor_encode(float(addr), 'numeric')
                    entry = {
                        'sedenion':  sed,
                        'signature': f"(C function at 0x{addr:016x})",
                        'doc':       f"PtolC compiled function {fn_name}",
                        'source':    '',
                        'peak_dim':  max(range(16), key=lambda k: abs(sed[k])),
                        'operator':  _OP.get(
                            max(range(16), key=lambda k: abs(sed[k])), 'unknown'),
                    }
                    with self._book._lock:
                        self._book._book[f"PtolC.{fn_name}.addr"] = entry
                    count += 1
                except AttributeError:
                    continue
            self._log(f"sniffed C binary {lib_path}: {count} symbols")
            return count
        except Exception as exc:
            self._log(f"C binary sniff failed: {exc}")
            return 0

    # ── Layer 3: Sedenion algebra corpus ──────────────────────────────────

    def algebra_corpus(self) -> str:
        """
        Generate the sedenion multiplication table in prose.
        All 256 entries. This IS Ptolemy reading his own instruction set.

        Each entry: "e{i} multiplied by e{j} gives {sign}e{k}: {op_i} times
        {op_j} gives {op_k} — [semantic interpretation]"

        :returns: Prose corpus of 256 multiplication facts.
        :rtype: str
        """
        # Import the sedenion table from monad
        try:
            from monad import _SED, _OP as _op_map
        except ImportError:
            return ''

        lines = []

        # Preamble: the operators and their roles
        lines.append(
            "The sedenion has sixteen dimensions each corresponding to a "
            "fundamental computational and linguistic operation."
        )
        for k, name in _op_map.items():
            # Map operator to natural language role
            roles = {
                0:  "the ground state identity no-op scalar bias unit element",
                1:  "negation complement inversion reversal the forbidden the not",
                2:  "binding association connection edge glue tissue conjunction",
                3:  "naming reference identification labeling pointing declaration",
                4:  "application execution calling invocation function evaluation",
                5:  "abstraction generalization pattern finding classification type",
                6:  "branching conditional choice gate if-then alternative selection",
                7:  "iteration sequence looping repetition temporal succession for-each",
                8:  "recursion self-reference depth stack fixpoint self-application",
                9:  "allocation fetch memory storage resource acquisition load save",
                10: "query search find lookup retrieve where what which pointer",
                11: "dereference follow anaphor pronoun resolution pointer following",
                12: "composition chaining pipeline then-after sequence-of F-then-G",
                13: "parallelization concurrent simultaneous three-face wankel and-also",
                14: "interrupt signal exception halt affect attention emotional charge",
                15: "emission output speaking return result the word the answer",
            }
            lines.append(
                f"e{k} is the {name} operator: "
                f"{roles.get(k, name)}"
            )

        lines.append("")
        lines.append(
            "The sedenion multiplication table defines how operators compose. "
            "Every computable function is a path through this table."
        )
        lines.append("")

        # All 256 multiplication entries
        for i in range(16):
            for j in range(16):
                sign, k = _SED[i][j]
                op_i = _op_map.get(i, f"e{i}")
                op_j = _op_map.get(j, f"e{j}")
                op_k = _op_map.get(k, f"e{k}")
                sign_word = "positive" if sign > 0 else ("negative" if sign < 0 else "zero")
                interp    = _mul_interpretation(i, j, k, sign)
                lines.append(
                    f"e{i} multiplied by e{j} gives {sign_word} e{k}: "
                    f"{op_i} times {op_j} gives {op_k}. {interp}"
                )

        # Key constants with semantic meaning
        lines.append("")
        lines.append(
            f"OMEGA_ZS equals {OMEGA_ZS} the Lambert W of one "
            f"the BAO spectral gap the idle RPM the sedenion Laplacian "
            f"spectral gap the cardioid base state the attractor."
        )
        lines.append(
            f"GAP equals {GAP} the Yang-Mills mass gap "
            f"the semantic vacuum floor the minimum beta value "
            f"the ground zero of the field."
        )
        lines.append(
            f"SIGMA_CRIT equals {SIGMA_CRIT} the critical line "
            f"sigma equals one half pi over two of the cardioid "
            f"the fixed point of the pi rotation the next word boundary."
        )
        lines.append(
            f"PHI equals {PHI:.6f} the golden ratio "
            f"the non-resonant walk step the irrational number "
            f"that prevents periodicity in the word selection."
        )

        return '\n'.join(lines)

    def code_corpus(self) -> str:
        """
        Generate prose corpus from the address book for ingestion into
        monad_sedenion.bin.

        :returns: Prose text.
        :rtype: str
        """
        return self._book.corpus_text()

    # ── monad_sedenion.bin builder ────────────────────────────────────────

    def build_sedenion_bin(self, output_path: str,
                           include_stdlib: bool = True,
                           c_source_dir: str = None) -> dict:
        """
        Full build pipeline for monad_sedenion.bin.

        Phase 1: Sniff Ptolemy's own skills
        Phase 2: Sniff stdlib modules
        Phase 3: Sniff C source (if c_source_dir provided)
        Phase 4: Generate algebra corpus (multiplication table in prose)
        Phase 5: Generate code corpus from address book
        Phase 6: Ingest all corpora into engine
        Phase 7: Save as monad_sedenion.bin

        :param output_path: Destination .bin file path.
        :param include_stdlib: If True, include stdlib modules.
        :param c_source_dir: Path to PtolC source directory (optional).
        :returns: Build stats dict.
        :rtype: dict
        """
        stats = {'callables': 0, 'algebra_lines': 0, 'code_lines': 0,
                 'vocab_before': self._engine.crank.n}

        # Phase 1: Ptolemy's own skills
        self._log("Phase 1: sniffing Ptolemy skills...")
        stats['callables'] += self.sniff_self()

        # Phase 2: stdlib
        if include_stdlib:
            self._log("Phase 2: sniffing stdlib...")
            stats['callables'] += self.sniff_stdlib()

        # Phase 3: C source
        if c_source_dir:
            self._log("Phase 3: sniffing C source...")
            c_dir = Path(c_source_dir)
            for c_file in c_dir.glob('**/*.c'):
                self.sniff_c_source(str(c_file))
            for h_file in c_dir.glob('**/*.h'):
                self.sniff_c_source(str(h_file))
            # Try compiled .so
            for so_file in c_dir.glob('**/*.so'):
                self.sniff_c_numeric(str(so_file))

        # Phase 4: Algebra corpus
        self._log("Phase 4: generating algebra corpus...")
        algebra = self.algebra_corpus()
        stats['algebra_lines'] = len(algebra.splitlines())
        self._engine.crank.learn(algebra)

        # Phase 5: Code corpus
        self._log("Phase 5: generating code corpus...")
        code_text = self.code_corpus()
        stats['code_lines'] = len(code_text.splitlines())
        self._engine.crank.learn(code_text)

        # Phase 6: Save address book alongside bin
        book_path = output_path.replace('.bin', '_addresses.pkl')
        self._book.save(book_path)
        self._log(f"Address book saved: {book_path}")

        # Phase 7: Save engine state as monad_sedenion.bin
        result = self._engine.save_session(output_path)
        stats['vocab_after']   = self._engine.crank.n
        stats['words_added']   = stats['vocab_after'] - stats['vocab_before']
        stats['saved']         = result.get('saved', output_path)
        self._log(
            f"monad_sedenion.bin built: {stats['callables']} callables, "
            f"{stats['words_added']} new words, "
            f"vocab={stats['vocab_after']}"
        )
        return stats

    # ── Query interface ───────────────────────────────────────────────────

    def nearest_callable(self, query: str, n: int = 5) -> list:
        """
        Find n callables nearest to a code-semantic query string.

        Uses _code_encode so that 'fetch url' → e9_allocate neighborhood,
        not the e3_name dominated result from cam_encode.

        :param query: Code concept string ('fetch url', 'emit output', etc.).
        :param n: Number of results.
        :returns: List of (callable_name, similarity, operator) tuples.
        :rtype: list
        """
        return self._book.nearest_code(query, n)

    def nearest_callable_by_sed(self, sedenion: list, n: int = 5) -> list:
        """
        Find n callables nearest to a pre-computed sedenion vector.
        The vector MUST be from _code_encode, not cam_encode.

        :param sedenion: 16-float code-encoded sedenion.
        :param n: Number of results.
        :returns: List of (callable_name, similarity, operator) tuples.
        :rtype: list
        """
        return self._book.nearest(sedenion, n)

    def callable_sedenion(self, full_name: str) -> Optional[list]:
        """
        Look up sedenion coordinate for a known callable by name.

        :param full_name: e.g. 'urllib.request.urlopen'
        :returns: 16-float sedenion vector or None.
        :rtype: list or None
        """
        with self._book._lock:
            entry = self._book._book.get(full_name)
            if entry:
                return entry['sedenion']
        return None

    def operator_neighborhood(self, op_idx: int) -> list:
        """
        All callables living in sedenion dimension op_idx neighborhood.

        :param op_idx: Sedenion dimension 0-15.
        :returns: [(callable_name, peak_value), ...]
        :rtype: list
        """
        return self._book.operator_cluster(op_idx)

    def report(self) -> str:
        """
        Print operator neighborhood map.
        Shows which callables live in which sedenion dimension.

        :returns: Formatted report string.
        :rtype: str
        """
        lines = ['=== Sedenion Address Map ===']
        with self._book._lock:
            total = len(self._book._book)
        lines.append(f"Total callables mapped: {total}")
        lines.append('')
        for op_idx in range(16):
            cluster = self.operator_neighborhood(op_idx)
            op_name = _OP.get(op_idx, f'e{op_idx}')
            lines.append(f"e{op_idx:2d} {op_name:13s} [{len(cluster):3d} callables]")
            for name, peak_val in cluster[:5]:
                lines.append(f"     {name:<55s} ψ={peak_val:.4f}")
            if len(cluster) > 5:
                lines.append(f"     ... and {len(cluster) - 5} more")
        return '\n'.join(lines)

    @property
    def address_book(self) -> SedenionAddressBook:
        """Direct access to the address book."""
        return self._book


def _mul_interpretation(i: int, j: int, k: int, sign: int) -> str:
    """
    Generate a semantic interpretation of one sedenion multiplication entry.
    Maps algebraic relationships to computational/linguistic meaning.

    :param i: Left operand index.
    :param j: Right operand index.
    :param k: Result index.
    :param sign: +1, -1, or 0.
    :returns: Interpretation string.
    :rtype: str
    """
    if sign == 0:
        return "Zero result — zero divisor boundary."
    op_i = _OP.get(i, f'e{i}')
    op_j = _OP.get(j, f'e{j}')
    op_k = _OP.get(k, f'e{k}')
    neg  = "the anticommutative reversal of " if sign < 0 else ""

    # Specific meaningful interpretations for key products
    interp_map = {
        (9,  3):  "allocating a named resource: fetch by URL",          # alloc × name
        (3,  9):  "naming an allocated resource: assign to variable",   # name × alloc
        (9,  11): "allocating via dereference: fetch what pointer refers to",
        (10, 3):  "querying by name: search for the named thing",
        (10, 9):  "querying for allocation: find the resource to fetch",
        (4,  11): "applying to a dereferenced value: call function on pointer target",
        (12, 11): "composing with dereference: pipeline that follows references",
        (7,  10): "iterating a query: loop over search results",
        (7,  4):  "iterating application: map function over sequence",
        (8,  4):  "recursive application: self-applying function",
        (6,  15): "conditional emit: if-then return",
        (5,  3):  "abstracting a name: generalising from specific reference",
        (13, 4):  "parallelising application: concurrent function calls",
        (15, 9):  "emitting an allocation: return a fetched resource",
        (2,  3):  "binding a name: variable assignment",
        (11, 3):  "dereferencing a name: following a named pointer",
    }
    specific = interp_map.get((i, j), '')
    if specific:
        return f"{neg}{specific}"
    return (
        f"{neg}{op_i} composed with {op_j} produces {op_k} "
        f"in the sedenion algebra."
    )


# ═════════════════════════════════════════════════════════════════════════════
# SkillBook — Yellow Pages / Sedenion DNS
# ═════════════════════════════════════════════════════════════════════════════
#
# The AddressBook is the White Pages: "who IS urllib.request.urlopen?"
# The SkillBook is the Yellow Pages: "I need to FETCH A URL — what skill does that?"
#
# The sedenion IS the IP address.
# The skill name IS the domain name.
# SkillBook.resolve() IS DNS resolution.
#
# Architecture (octonion groupings):
#   e0–e3   Object quaternion  — identity, negate, bind, name
#   e4–e7   Flow quaternion    — apply, abstract, branch, iterate
#   e8–e11  Memory quaternion  — recurse, allocate, query, dereference
#   e12–e15 System quaternion  — compose, parallelize, interrupt, emit
#
# A skill's sedenion IP encodes WHICH QUATERNION FACE it lives on,
# and precisely WHERE within that face.  Ptolemy navigates skill-space
# the same way he navigates semantic-space: by following the field gradient.
#
# ═════════════════════════════════════════════════════════════════════════════

_QUATERNION_FACES = {
    'object': (0, 1, 2, 3),    # identity negate bind name
    'flow':   (4, 5, 6, 7),    # apply abstract branch iterate
    'memory': (8, 9, 10, 11),  # recurse allocate query dereference
    'system': (12, 13, 14, 15), # compose parallelize interrupt emit
}


class SkillEntry:
    """
    One registered skill in the SkillBook.

    :param name: Human-readable skill name ('fetch a URL from the web').
    :param ip: Sedenion IP (16 floats from _code_encode).
    :param callables: List of callable names that implement this skill.
    :param tags: Free-form tags for search/filtering.
    :param module: Python module path (e.g. 'skills.search').
    :param description: Prose description of what this skill does.
    """

    __slots__ = ('name', 'ip', 'callables', 'tags', 'module', 'description')

    def __init__(self, name: str, ip: list, callables: list = None,
                 tags: list = None, module: str = '',
                 description: str = ''):
        self.name        = name
        self.ip          = ip           # sedenion address
        self.callables   = callables or []
        self.tags        = tags or []
        self.module      = module
        self.description = description

    def face(self) -> str:
        """
        Which quaternion face does this skill live on?

        :returns: 'object', 'flow', 'memory', or 'system'.
        :rtype: str
        """
        face_scores = {}
        for face_name, dims in _QUATERNION_FACES.items():
            face_scores[face_name] = sum(abs(self.ip[d]) for d in dims)
        return max(face_scores, key=face_scores.get)

    def octonion(self) -> tuple:
        """
        Which octonion half? Lower (e0-e7) or upper (e8-e15)?

        :returns: Tuple (half_name, strength).
        :rtype: tuple
        """
        lower = sum(abs(self.ip[d]) for d in range(8))
        upper = sum(abs(self.ip[d]) for d in range(8, 16))
        if lower >= upper:
            return ('lower', lower)
        return ('upper', upper)

    def profile(self) -> str:
        """
        Two-line human-readable sedenion IP profile.

        :returns: Profile string.
        :rtype: str
        """
        top4 = sorted(range(16), key=lambda k: -abs(self.ip[k]))[:4]
        dims = ' '.join(f'e{k}({_OP[k][:5]}={self.ip[k]:.3f})' for k in top4)
        face = self.face()
        octs, oct_s = self.octonion()
        return f"[{face}/{octs}]  {dims}"


class SkillBook:
    """
    Sedenion DNS — resolves skill queries to sedenion IPs and back.

    White Pages (AddressBook) answers: "What sedenion coordinate IS urllib.request.urlopen?"
    Yellow Pages (SkillBook) answers:  "I need to FETCH A URL — which skill handles that?"

    The 16 sedenion dimensions form 4 quaternion faces:
      Object (e0-e3):  identity/naming/binding operations
      Flow   (e4-e7):  application/branching/iteration
      Memory (e8-e11): recursion/allocation/query/dereference
      System (e12-e15): composition/parallelism/interrupt/emit

    Two octonions (e0-e7 lower, e8-e15 upper) give coarse routing;
    the full 16-dim IP gives fine-grained skill location.

    :param address_book: Optional SedenionAddressBook for callable cross-reference.
    """

    def __init__(self, address_book: SedenionAddressBook = None):
        self._skills   = {}    # name → SkillEntry
        self._by_face  = {f: [] for f in _QUATERNION_FACES}
        self._lock     = threading.Lock()
        self._book     = address_book

    def register(self, name: str, description: str,
                 callables: list = None, tags: list = None,
                 module: str = '') -> 'SkillEntry':
        """
        Register a skill. The sedenion IP is computed from description
        using _code_encode (structural encoder).

        :param name: Human-readable skill name.
        :param description: What this skill DOES (used for IP computation).
        :param callables: List of callable names implementing this skill.
        :param tags: Search tags.
        :param module: Python module path.
        :returns: The registered SkillEntry.
        :rtype: SkillEntry
        """
        ip = _code_encode(description, depth=-1)  # -1 = no identity bias
        entry = SkillEntry(name=name, ip=ip, callables=callables or [],
                           tags=tags or [], module=module,
                           description=description)
        with self._lock:
            self._skills[name] = entry
            face = entry.face()
            if name not in self._by_face[face]:
                self._by_face[face].append(name)
        return entry

    def resolve(self, query: str, n: int = 5) -> list:
        """
        DNS resolution: query string → n nearest skills.

        'How do I fetch a URL?' → [('fetch from web', sim=0.94, face='memory'), ...]

        :param query: Human-readable capability request.
        :param n: Number of results.
        :returns: List of (skill_name, similarity, face) tuples.
        :rtype: list
        """
        q_ip = _code_encode(query, depth=-1)
        results = []
        with self._lock:
            for name, entry in self._skills.items():
                sim = _cosine_similarity(q_ip, entry.ip)
                results.append((sim, name, entry.face()))
        results.sort(reverse=True)
        return [(name, sim, face) for sim, name, face in results[:n]]

    def dns_lookup(self, skill_name: str) -> Optional[list]:
        """
        Forward DNS: skill name → sedenion IP.

        :param skill_name: Registered skill name.
        :returns: 16-float sedenion IP or None.
        :rtype: list or None
        """
        with self._lock:
            entry = self._skills.get(skill_name)
            return entry.ip if entry else None

    def reverse_dns(self, ip: list, n: int = 1) -> list:
        """
        Reverse DNS: sedenion IP → nearest skill names.

        :param ip: 16-float sedenion IP.
        :param n: Number of results.
        :returns: List of (skill_name, similarity) tuples.
        :rtype: list
        """
        results = []
        with self._lock:
            for name, entry in self._skills.items():
                sim = _cosine_similarity(ip, entry.ip)
                results.append((sim, name))
        results.sort(reverse=True)
        return [(name, sim) for sim, name in results[:n]]

    def face_skills(self, face: str) -> list:
        """
        All skills on a given quaternion face.

        :param face: 'object', 'flow', 'memory', or 'system'.
        :returns: List of skill names on that face.
        :rtype: list
        """
        with self._lock:
            return list(self._by_face.get(face, []))

    def callables_for(self, query: str, n: int = 10) -> list:
        """
        Find callables that implement the skill nearest to a query.
        Crosses Yellow Pages → White Pages: skill DNS → callable lookup.

        :param query: Capability description.
        :param n: Max callables to return.
        :returns: List of callable names.
        :rtype: list
        """
        skills = self.resolve(query, n=3)
        seen = set()
        result = []
        for skill_name, _sim, _face in skills:
            entry = self._skills.get(skill_name)
            if entry:
                for c in entry.callables:
                    if c not in seen:
                        seen.add(c)
                        result.append(c)
                        if len(result) >= n:
                            return result
        return result

    def save(self, path: str):
        """
        Persist SkillBook to disk.

        :param path: Output path.
        """
        with self._lock:
            data = {s.name: {
                'ip': s.ip, 'callables': s.callables,
                'tags': s.tags, 'module': s.module,
                'description': s.description,
            } for s in self._skills.values()}
        with open(path, 'wb') as fh:
            pickle.dump({'skills': data, 'version': 1}, fh)

    def load(self, path: str) -> bool:
        """
        Load SkillBook from disk.

        :param path: Input path.
        :returns: True on success.
        :rtype: bool
        """
        try:
            with open(path, 'rb') as fh:
                data = pickle.load(fh)
            for name, d in data.get('skills', {}).items():
                entry = SkillEntry(
                    name=name, ip=d['ip'],
                    callables=d.get('callables', []),
                    tags=d.get('tags', []),
                    module=d.get('module', ''),
                    description=d.get('description', ''),
                )
                self._skills[name] = entry
                face = entry.face()
                if name not in self._by_face[face]:
                    self._by_face[face].append(name)
            return True
        except Exception:
            return False

    def report(self) -> str:
        """
        Full SkillBook directory listing, organized by quaternion face.

        :returns: Formatted report string.
        :rtype: str
        """
        lines = ['╔══════════════════════════════════════════════════════╗',
                 '║           PTOLEMY SKILLBOOK — SEDENION DNS           ║',
                 '╚══════════════════════════════════════════════════════╝']
        with self._lock:
            total = len(self._skills)
        lines.append(f"  {total} skills registered\n")
        for face_name, dims in _QUATERNION_FACES.items():
            dim_labels = ' '.join(f'e{d}({_OP[d][:5]})' for d in dims)
            skills_on_face = self.face_skills(face_name)
            lines.append(f"▶ {face_name.upper()} FACE [{dim_labels}]"
                         f"  ({len(skills_on_face)} skills)")
            with self._lock:
                for sname in skills_on_face:
                    entry = self._skills[sname]
                    prof  = entry.profile()
                    lines.append(f"    {sname}")
                    lines.append(f"      {prof}")
                    lines.append(f"      → {entry.description[:80]}")
            lines.append('')
        return '\n'.join(lines)

    def register_ptolemy_skills(self):
        """
        Seed the SkillBook with all of Ptolemy's built-in skills.
        This IS Ptolemy's self-knowledge of his own capabilities.

        :returns: Number of skills registered.
        :rtype: int
        """
        skills = [
            # ── Object face (e0-e3): naming, binding, identity ──────────
            ('identify word type',
             'name label identify classify type token word symbol',
             ['skills.lexicon.PtolLexicon.fetch_word_meta',
              'skills.lexicon.PtolLexicon.topology_text'],
             ['lexicon', 'wiktionary'], 'skills.lexicon'),

            ('bind sedenion to word',
             'bind associate connect name label register word vector',
             ['monad.cam_encode', 'monad.sensor_encode'],
             ['encoding', 'sedenion'], 'monad'),

            # ── Flow face (e4-e7): apply, abstract, branch, iterate ──────
            ('apply sedenion algebra',
             'apply execute multiply sedenion algebra operator',
             ['monad.Engine.fire', 'monad.Engine.score'],
             ['algebra', 'sedenion', 'engine'], 'monad'),

            ('abstract pattern from text',
             'abstract generalize classify pattern type schema text chunk',
             ['monad.Crank.learn', 'monad.Engine.ingest'],
             ['learning', 'abstraction'], 'monad'),

            ('branch on field health',
             'branch conditional check validate field health BAO threshold',
             ['skills.draw.HamiltonianReport.field_state'],
             ['bao', 'health', 'diagnostics'], 'skills.draw'),

            ('iterate over corpus',
             'iterate loop sequence each map scan walk corpus text chunk',
             ['monad.TeachingThread.run',
              'skills.crawler.PtolCrawler.fetch'],
             ['teaching', 'crawl', 'iterate'], 'monad'),

            # ── Memory face (e8-e11): recurse, allocate, query, deref ───
            ('recurse into deep structure',
             'recurse self depth stack nested tree fixpoint recursive',
             ['monad.Engine.j_mu', 'monad.Engine.a_propagate'],
             ['sedenion', 'field', 'deep'], 'monad'),

            ('fetch text from URL',
             'fetch get open download url http ftp request acquire',
             ['skills.search.PtolSearch.next_url',
              'skills.crawler.PtolCrawler.fetch',
              'urllib.request.urlopen'],
             ['network', 'fetch', 'crawl'], 'skills.search'),

            ('fetch academic paper',
             'search query find fetch download academic paper doi arxiv scholar pubmed research',
             ['skills.scholar.PtolScholar.fetch_unpaywall',
              'skills.scholar.PtolScholar.search_semantic_scholar',
              'skills.scholar.PtolScholar.search_arxiv'],
             ['scholar', 'academic', 'fetch'], 'skills.scholar'),

            ('query sedenion field',
             'query search find lookup sedenion beta field word nearest',
             ['monad.Crank.query', 'monad.Engine.score'],
             ['query', 'sedenion', 'field'], 'monad'),

            ('resolve sedenion address',
             'dereference resolve follow pointer reference sedenion address skill',
             ['skills.apisniff.SkillBook.resolve',
              'skills.apisniff.SkillBook.dns_lookup',
              'skills.apisniff.SedenionAddressBook.nearest_code'],
             ['dns', 'skillbook', 'address'], 'skills.apisniff'),

            # ── System face (e12-e15): compose, parallel, interrupt, emit
            ('compose skill pipeline',
             'compose chain pipe sequence pipeline then after combine merge',
             ['skills.sources.PtolSources.seed_active',
              'monad.TeachingThread._build_teach_stack'],
             ['pipeline', 'compose', 'sources'], 'skills.sources'),

            ('run parallel daemon threads',
             'parallelize concurrent thread async pool worker daemon socket',
             ['monad.TeachingThread',
              'skills.network.PtolNetwork'],
             ['daemon', 'thread', 'parallel'], 'monad'),

            ('emit hamiltonian report',
             'emit output report hamiltonian sedenion UNS coordinates location',
             ['skills.draw.HamiltonianReport.render_text',
              'skills.draw.HamiltonianReport.print_report'],
             ['hamiltonian', 'report', 'emit'], 'skills.draw'),

            ('emit spoken word',
             'emit output generate speak produce word token sentence text',
             ['monad.Crank.emit', 'monad.Engine.generate'],
             ['speaking', 'generate', 'emit'], 'monad'),

            ('signal interrupt exception',
             'interrupt signal exception error raise halt abort cancel',
             ['skills.monitor.PtolMonitor.check_resources'],
             ['error', 'interrupt', 'monitor'], 'skills.monitor'),

            ('draw sedenion field',
             'draw render plot visualize sedenion BAO ring field diagram',
             ['skills.draw.PtolDraw.bao_rings_svg',
              'skills.draw.PtolDraw.sedenion_wheel',
              'skills.draw.PtolDraw.field_health_plot'],
             ['draw', 'visualize', 'bao'], 'skills.draw'),

            ('load and save sedenion state',
             'load save read write serialize checkpoint session state bin',
             ['monad.Engine.load_bin', 'monad.Engine.save_session',
              'monad.Engine.load_session'],
             ['checkpoint', 'save', 'load'], 'monad'),

            ('seed corpus from Gutenberg',
             'fetch get download Gutenberg English text plain book seed',
             ['skills.search.PtolSearch.seed_gutenberg'],
             ['gutenberg', 'corpus', 'seed'], 'skills.search'),

            ('seed corpus from archive.org',
             'fetch get download archive internet text seed corpus scan',
             ['skills.search.PtolSearch.seed_archive'],
             ['archive', 'corpus', 'seed'], 'skills.search'),

            ('learn word topology from Wiktionary',
             'learn study ingest wiktionary lexicon word definition synonym antonym etymology topology language',
             ['skills.lexicon.PtolLexicon.seed_common_words',
              'skills.lexicon.PtolLexicon.demand_word'],
             ['wiktionary', 'lexicon', 'topology'], 'skills.lexicon'),

            ('map callable to sedenion address',
             'inspect browse dir enumerate callable function sedenion code address api introspect sniff',
             ['skills.apisniff.APISniff.sniff_module',
              'skills.apisniff.APISniff.build_sedenion_bin'],
             ['apisniff', 'code', 'address'], 'skills.apisniff'),
        ]
        count = 0
        for item in skills:
            name, desc = item[0], item[1]
            callables = item[2] if len(item) > 2 else []
            tags      = item[3] if len(item) > 3 else []
            module    = item[4] if len(item) > 4 else ''
            self.register(name, desc, callables, tags, module)
            count += 1
        return count
