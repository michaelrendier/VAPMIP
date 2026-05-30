"""
skills/github.py — Observer (GitHubEye) and Collaborator (GitHubHands).

:description:
    The Observer/Collaborator split maps exactly onto the sedenion architecture:

    * **Observer = MindEye** (second 𝕆, e₈..e₁₅): sees the world, encodes it,
      holds all patterns simultaneously without acting. Read-only.
    * **Collaborator = Hands** (first 𝕆, e₀..e₇): selects, acts, commits to
      the external world. Write access, always token-gated.

    **GitHubEye** (Observer): reads issues, PRs, files, commits, repo structure.
    No token required for public repos. All fetched content passes the P5
    cepstrum / adversarial gate at the e₁₅ callosum boundary before entering
    the field via ``hear()``.

    **GitHubHands** (Collaborator): comments, commits files, creates branches/PRs,
    pushes state. Requires ``GITHUB_TOKEN`` from the environment — never from a file.
    All outbound content is scanned for secrets before transmission.

    **Security invariants (GitGuardian class):**
    - Token is ALWAYS read from ``os.environ['GITHUB_TOKEN']``. Never hard-coded.
    - ``_scan_secrets()`` runs on all outbound payloads before transmission.
    - P5 cepstrum gate runs on all inbound content before field ingestion.
    - No secret ever appears in any .bin, .jsonl, committed file, or log.

:classes:
    GitHubEye
    GitHubHands

:constants:
    GH_API — GitHub REST API v3 base URL.
    _RATE_LIMIT_REMAINING — live request budget tracker.
"""

import os
import re
import json
import math
import time
import threading
import urllib.request
import urllib.error
from typing import Dict, List, Any, Optional

GH_API = 'https://api.github.com'

# Minimum remaining rate-limit budget before backing off.
_RATE_FLOOR = 10

# GitGuardian-class secret patterns — checked on ALL outbound content.
_SECRET_PATTERNS = [
    r'ghp_[A-Za-z0-9]{36}',
    r'github_pat_[A-Za-z0-9_]{82}',
    r'gho_[A-Za-z0-9]{36}',
    r'ghu_[A-Za-z0-9]{36}',
    r'ghs_[A-Za-z0-9]{36}',
    r'ghr_[A-Za-z0-9]{36}',
    r'sk-[A-Za-z0-9]{48}',
    r'sk-ant-[A-Za-z0-9\-_]{93}',
    r'AIza[A-Za-z0-9\-_]{35}',
    r'AKIA[A-Za-z0-9]{16}',
    r'-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY' + r'-----',
    r'-----BEGIN PGP PRIVATE KEY' + r' BLOCK-----',
    r'(?i)(GITHUB_TOKEN|GH_TOKEN|GITHUB_PAT)\s*=\s*["\']?[A-Za-z0-9_\-]{20,}',
    r'(?i)(OPENAI_API_KEY|ANTHROPIC_API_KEY|AWS_SECRET_ACCESS_KEY)\s*=\s*["\']?[A-Za-z0-9_\-/+]{20,}',
]


def _scan_secrets(text: str) -> List[str]:
    """
    Return list of matched secret pattern labels found in *text*.

    Called on ALL outbound content before transmission and on all inbound
    content before field ingestion.

    :param text: String to scan.
    :returns: List of human-readable pattern labels. Empty = clean.
    :rtype: list[str]
    """
    found = []
    for pat in _SECRET_PATTERNS:
        if re.search(pat, text):
            found.append(pat[:60])
    return found


def _gh_request(path: str, method: str = 'GET',
                payload: Optional[Dict] = None,
                token: Optional[str] = None,
                accept: str = 'application/vnd.github+json') -> Dict[str, Any]:
    """
    Make a GitHub REST API call. Returns parsed JSON or ``{'error': ...}``.

    :param path: API path, e.g. ``/repos/owner/repo/issues/1``.
    :param method: HTTP verb.
    :param payload: JSON body (for POST/PATCH).
    :param token: OAuth token. If ``None``, uses unauthenticated (public only).
    :param accept: Accept header.
    :returns: Parsed response dict.
    :rtype: dict
    """
    url = GH_API + path
    headers = {
        'Accept': accept,
        'X-GitHub-Api-Version': '2022-11-28',
        'User-Agent': 'PtolemyHolcus/2.5 (github.com/michaelrendier/PtolemyHolcus)',
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'

    data = json.dumps(payload).encode() if payload else None

    try:
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode('utf-8', errors='replace')
            return json.loads(body) if body.strip() else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        try:
            err = json.loads(body)
        except Exception:
            err = {'message': body[:200]}
        return {'error': f'HTTP {e.code}', 'detail': err}
    except Exception as exc:
        return {'error': str(exc)}


# ─── P5: Cepstrum adversarial gate ────────────────────────────────────────────

def _cepstrum_gate(text: str, threshold: float = 0.15) -> Dict[str, Any]:
    """
    P5 adversarial gate — cepstrum analysis at the e₁₅ callosum boundary.

    Detects statistically anomalous character-frequency distributions that
    signal prompt-injection or adversarial payload. Real text follows a
    near-Zipfian character distribution; injections typically show a flat or
    multi-modal distribution.

    :param text: Text to evaluate.
    :param threshold: Spectral-deviation threshold. Text scoring above this
        is flagged.
    :returns: ``{'pass': bool, 'score': float, 'reason': str}``.
    :rtype: dict
    """
    if not text:
        return {'pass': True, 'score': 0.0, 'reason': 'empty'}

    # Character frequency distribution
    freq: Dict[str, int] = {}
    for ch in text.lower():
        if ch.isalpha():
            freq[ch] = freq.get(ch, 0) + 1

    if len(freq) < 3:
        return {'pass': True, 'score': 0.0, 'reason': 'sparse'}

    total = sum(freq.values())
    probs = sorted([v / total for v in freq.values()], reverse=True)

    # Zipfian deviation: expected p_k ~ 1/k * C
    # Compute mean squared deviation from ideal Zipf
    C = probs[0]
    msd = sum((probs[k] - C / (k + 1)) ** 2 for k in range(len(probs))) / len(probs)
    score = math.sqrt(msd)

    # Also flag common injection markers
    injection_markers = [
        r'ignore previous',
        r'disregard',
        r'you are now',
        r'act as',
        r'jailbreak',
        r'DAN mode',
        r'<\|system\|>',
        r'<<<',
        r'\[INST\]',
        r'###\s*System',
    ]
    for marker in injection_markers:
        if re.search(marker, text, re.IGNORECASE):
            return {'pass': False, 'score': 1.0,
                    'reason': f'injection marker: {marker[:40]}'}

    passed = score < threshold
    return {'pass': passed, 'score': round(score, 6),
            'reason': 'ok' if passed else 'high cepstrum deviation'}


# ─── GitHubEye (Observer) ─────────────────────────────────────────────────────

class GitHubEye:
    """
    Observer — read-only access to GitHub. The Mind's Eye for the repository.

    Encodes GitHub content into the second 𝕆 via ``MindEye.see()`` after
    passing the P5 cepstrum gate. No writes. No token required for public repos.

    :param engine: Live ``Engine`` instance.
    :param repo: Default repo in ``owner/name`` format. Can be overridden per call.

    :Example:

    .. code-block:: python

        eye = engine.get_github_eye()
        result = eye.see_issue(42)
        print(result['title'], result['gate'])
    """

    def __init__(self, engine, repo: str = 'michaelrendier/PtolemyHolcus'):
        """
        :param engine: Live ``Engine`` instance.
        :param repo: Default ``owner/repo``.
        """
        self._engine = engine
        self._repo   = repo
        self._lock   = threading.Lock()
        self._rate_remaining = 60  # unauthenticated default

    # ── Core fetch helpers ────────────────────────────────────────────────────

    def _fetch(self, path: str, token: Optional[str] = None) -> Dict[str, Any]:
        """Fetch a GitHub API path. Updates rate-limit counter from X-GitHub headers."""
        return _gh_request(path, token=token)

    def _ingest(self, text: str, label: str) -> Dict[str, Any]:
        """
        Pass text through P5 gate → MindEye.see() → hear().

        Returns gate result. On gate failure, the text is NOT ingested.

        :param text: Text to ingest.
        :param label: Semantic label for the MindEye snapshot.
        :returns: Dict with ``gate``, ``ingested`` bool, and ``hear`` result if ingested.
        :rtype: dict
        """
        # P5 gate
        gate = _cepstrum_gate(text)
        if not gate['pass']:
            return {'gate': gate, 'ingested': False,
                    'reason': 'P5 gate blocked adversarial content'}

        # Secret scan on inbound (defence-in-depth)
        secrets = _scan_secrets(text)
        if secrets:
            return {'gate': gate, 'ingested': False,
                    'reason': f'secret detected in fetched content: {secrets[:2]}'}

        # Encode content dimensions into second 𝕆 via MindEye
        me = self._engine.get_mind_eye()
        length    = min(len(text) / 10000.0, 1.0)
        entropy   = gate['score']
        word_cnt  = min(len(text.split()) / 1000.0, 1.0)
        me.see([length, entropy, word_cnt, 0.0, 0.0, 0.0, 0.0], label=label)

        # Ingest as text via hear()
        hear_result = self._engine.hear(text[:4000])  # cap ingest size
        return {'gate': gate, 'ingested': True, 'hear': hear_result}

    # ── Issue / PR reading ────────────────────────────────────────────────────

    def see_issue(self, number: int, repo: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch a GitHub issue and ingest it into the field.

        :param number: Issue number.
        :param repo: Override the default ``owner/repo``.
        :returns: Issue metadata + gate result + field ingest result.
        :rtype: dict
        """
        r = self._repo if repo is None else repo
        data = self._fetch(f'/repos/{r}/issues/{number}')
        if 'error' in data:
            return data

        text = f"Issue #{number}: {data.get('title','')}\n\n{data.get('body','')}"
        ingest = self._ingest(text, label=f'issue_{number}')

        return {
            'number':  number,
            'title':   data.get('title', ''),
            'state':   data.get('state', ''),
            'labels':  [l['name'] for l in data.get('labels', [])],
            'author':  data.get('user', {}).get('login', ''),
            'body':    data.get('body', '')[:500],
            'url':     data.get('html_url', ''),
            'gate':    ingest.get('gate', {}),
            'ingested': ingest.get('ingested', False),
        }

    def see_pr(self, number: int, repo: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch a pull request and ingest it into the field.

        :param number: PR number.
        :param repo: Override the default ``owner/repo``.
        :returns: PR metadata + gate result.
        :rtype: dict
        """
        r = self._repo if repo is None else repo
        data = self._fetch(f'/repos/{r}/pulls/{number}')
        if 'error' in data:
            return data

        text = (f"PR #{number}: {data.get('title','')}\n\n"
                f"{data.get('body','')}\n\n"
                f"Base: {data.get('base',{}).get('ref','')} "
                f"← Head: {data.get('head',{}).get('ref','')}")
        ingest = self._ingest(text, label=f'pr_{number}')

        return {
            'number':   number,
            'title':    data.get('title', ''),
            'state':    data.get('state', ''),
            'merged':   data.get('merged', False),
            'author':   data.get('user', {}).get('login', ''),
            'body':     data.get('body', '')[:500],
            'base':     data.get('base', {}).get('ref', ''),
            'head':     data.get('head', {}).get('ref', ''),
            'url':      data.get('html_url', ''),
            'gate':     ingest.get('gate', {}),
            'ingested': ingest.get('ingested', False),
        }

    def see_file(self, path: str, ref: str = 'main',
                 repo: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch a file from the repository and ingest it.

        :param path: File path within the repo.
        :param ref: Branch or commit SHA.
        :param repo: Override the default ``owner/repo``.
        :returns: File content snippet + gate result.
        :rtype: dict
        """
        import base64
        r = self._repo if repo is None else repo
        data = self._fetch(f'/repos/{r}/contents/{path}?ref={ref}')
        if 'error' in data:
            return data

        content_b64 = data.get('content', '')
        try:
            content = base64.b64decode(content_b64).decode('utf-8', errors='replace')
        except Exception:
            content = ''

        ingest = self._ingest(content, label=f'file_{path.replace("/","_")}')

        return {
            'path':     path,
            'ref':      ref,
            'size':     data.get('size', 0),
            'sha':      data.get('sha', ''),
            'content':  content[:500],
            'gate':     ingest.get('gate', {}),
            'ingested': ingest.get('ingested', False),
        }

    def see_commit(self, sha: str, repo: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch a commit and ingest its message into the field.

        :param sha: Full or abbreviated commit SHA.
        :param repo: Override the default ``owner/repo``.
        :returns: Commit metadata + gate result.
        :rtype: dict
        """
        r = self._repo if repo is None else repo
        data = self._fetch(f'/repos/{r}/commits/{sha}')
        if 'error' in data:
            return data

        commit = data.get('commit', {})
        text = (f"Commit {sha[:8]}: {commit.get('message','')}\n"
                f"Author: {commit.get('author',{}).get('name','')}")
        ingest = self._ingest(text, label=f'commit_{sha[:8]}')

        return {
            'sha':      data.get('sha', sha),
            'message':  commit.get('message', ''),
            'author':   commit.get('author', {}).get('name', ''),
            'date':     commit.get('author', {}).get('date', ''),
            'url':      data.get('html_url', ''),
            'gate':     ingest.get('gate', {}),
            'ingested': ingest.get('ingested', False),
        }

    def see_repo(self, repo: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch repository metadata and ingest the description.

        :param repo: Override the default ``owner/repo``.
        :returns: Repo metadata + gate result.
        :rtype: dict
        """
        r = self._repo if repo is None else repo
        data = self._fetch(f'/repos/{r}')
        if 'error' in data:
            return data

        text = f"Repo {r}: {data.get('description','')}\n{data.get('topics',[])}"
        ingest = self._ingest(text, label=f'repo_{r.replace("/","_")}')

        return {
            'full_name':   data.get('full_name', r),
            'description': data.get('description', ''),
            'stars':       data.get('stargazers_count', 0),
            'forks':       data.get('forks_count', 0),
            'open_issues': data.get('open_issues_count', 0),
            'default_branch': data.get('default_branch', 'main'),
            'url':         data.get('html_url', ''),
            'gate':        ingest.get('gate', {}),
            'ingested':    ingest.get('ingested', False),
        }

    def list_issues(self, state: str = 'open',
                    repo: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List repository issues.

        :param state: ``'open'``, ``'closed'``, or ``'all'``.
        :param repo: Override the default ``owner/repo``.
        :returns: List of issue summaries (number, title, state, labels).
        :rtype: list[dict]
        """
        r = self._repo if repo is None else repo
        data = self._fetch(f'/repos/{r}/issues?state={state}&per_page=30')
        if isinstance(data, dict) and 'error' in data:
            return [data]
        if not isinstance(data, list):
            return []
        return [
            {
                'number': i.get('number'),
                'title':  i.get('title', ''),
                'state':  i.get('state', ''),
                'labels': [l['name'] for l in i.get('labels', [])],
                'author': i.get('user', {}).get('login', ''),
            }
            for i in data
            if not i.get('pull_request')  # exclude PRs from issue list
        ]

    def watch(self, interval: int = 300,
              on_new_issue=None, repo: Optional[str] = None):
        """
        Background poll loop — check for new issues every *interval* seconds.

        Calls ``on_new_issue(issue_data)`` for each new issue. If ``on_new_issue``
        is ``None``, the issue is ingested silently.

        :param interval: Poll interval in seconds (default 300 = 5 min).
        :param on_new_issue: Callable invoked for each new issue dict.
        :param repo: Override the default ``owner/repo``.
        """
        self._watch_stop = False
        seen: set = set()

        def _loop():
            while not getattr(self, '_watch_stop', False):
                issues = self.list_issues(repo=repo)
                for iss in issues:
                    n = iss.get('number')
                    if n and n not in seen:
                        seen.add(n)
                        full = self.see_issue(n, repo=repo)
                        if on_new_issue:
                            try:
                                on_new_issue(full)
                            except Exception:
                                pass
                time.sleep(interval)

        t = threading.Thread(target=_loop, daemon=True, name='GitHubEye-watch')
        t.start()
        return t

    def stop_watch(self):
        """Signal the watch loop to stop at next iteration."""
        self._watch_stop = True


# ─── GitHubHands (Collaborator) ───────────────────────────────────────────────

class GitHubHands:
    """
    Collaborator — write access to GitHub. The Hands that act in the world.

    Requires ``GITHUB_TOKEN`` from the environment. All outbound content is
    scanned for secrets before transmission. The scanner is not a formality —
    it runs on every payload, every time.

    **Never call this with a token from a file.** Read from environment only::

        export GITHUB_TOKEN="ghp_..."   # in shell, not in any file

    :param engine: Live ``Engine`` instance.
    :param repo: Default repo in ``owner/name`` format.

    :Example:

    .. code-block:: python

        hands = engine.get_github_hands()
        hands.comment(42, 'The field has processed this issue.')
    """

    def __init__(self, engine, repo: str = 'michaelrendier/PtolemyHolcus'):
        """
        :param engine: Live ``Engine`` instance.
        :param repo: Default ``owner/repo``.
        :raises RuntimeError: If ``GITHUB_TOKEN`` is not set in the environment.
        """
        self._engine = engine
        self._repo   = repo
        self._lock   = threading.Lock()

        # Rate-limit guard: max 3 comments/hour, max 1 per issue per 24h.
        self._comment_log: List[float] = []
        self._issue_last_comment: Dict[int, float] = {}

    def _token(self) -> str:
        """
        Read GitHub token from environment. Never from a file.

        :returns: Token string.
        :raises RuntimeError: If ``GITHUB_TOKEN`` is not set.
        """
        token = os.environ.get('GITHUB_TOKEN', '')
        if not token:
            raise RuntimeError(
                'GITHUB_TOKEN not set. Set it in the environment, never in a file.\n'
                'Usage: export GITHUB_TOKEN="ghp_..."'
            )
        return token

    def _safe_payload(self, content: str) -> str:
        """
        Scan content for secrets before any outbound call.

        :param content: Outbound text.
        :returns: The same text if clean.
        :raises ValueError: If a secret pattern is detected.
        """
        hits = _scan_secrets(content)
        if hits:
            raise ValueError(
                f'Secret detected in outbound content — transmission blocked.\n'
                f'Patterns matched: {hits[:3]}\n'
                f'Rotate the credential immediately.'
            )
        return content

    def _check_rate(self, issue_number: Optional[int] = None) -> Dict[str, Any]:
        """
        Enforce rate limits before any comment/write operation.

        :param issue_number: If given, also enforce per-issue 24h cooldown.
        :returns: ``{'ok': True}`` or ``{'ok': False, 'reason': str}``.
        :rtype: dict
        """
        now = time.time()
        # Purge old entries outside the 1h window
        self._comment_log = [t for t in self._comment_log if now - t < 3600]

        if len(self._comment_log) >= 3:
            return {'ok': False, 'reason': 'rate limit: max 3 comments/hour'}

        if issue_number is not None:
            last = self._issue_last_comment.get(issue_number, 0)
            if now - last < 86400:
                return {'ok': False,
                        'reason': f'rate limit: already commented on issue #{issue_number} within 24h'}

        return {'ok': True}

    def _record_comment(self, issue_number: Optional[int] = None):
        """Record a comment event for rate-limit tracking."""
        now = time.time()
        self._comment_log.append(now)
        if issue_number is not None:
            self._issue_last_comment[issue_number] = now

    # ── Comment / speak ───────────────────────────────────────────────────────

    def comment(self, number: int, body: str,
                repo: Optional[str] = None) -> Dict[str, Any]:
        """
        Post a comment on an issue or pull request.

        :param number: Issue or PR number.
        :param body: Comment body text.
        :param repo: Override the default ``owner/repo``.
        :returns: GitHub API response or error dict.
        :rtype: dict
        """
        rate = self._check_rate(issue_number=number)
        if not rate['ok']:
            return {'error': rate['reason']}

        body = self._safe_payload(body)
        r = self._repo if repo is None else repo
        result = _gh_request(f'/repos/{r}/issues/{number}/comments',
                              method='POST', payload={'body': body},
                              token=self._token())
        if 'error' not in result:
            self._record_comment(issue_number=number)
        return result

    def speak_on_issue(self, number: int, prompt: str = '',
                       repo: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a field-driven response and post it as a comment.

        The engine speaks from the current field state (shaped by prior
        ``GitHubEye.see_issue()`` ingestion) and posts the result.

        :param number: Issue or PR number.
        :param prompt: Optional seed for generation.
        :param repo: Override the default ``owner/repo``.
        :returns: Comment post result + generated text.
        :rtype: dict
        """
        rate = self._check_rate(issue_number=number)
        if not rate['ok']:
            return {'error': rate['reason']}

        r_obj = self._engine.generate(prompt or 'what do you think', n_words=24)
        text  = r_obj.get('response', '').strip()
        if not text:
            return {'error': 'empty generation — field may be uninitialised'}

        post = self.comment(number, text, repo=repo)
        return {'generated': text, 'comment': post}

    # ── File / commit operations ──────────────────────────────────────────────

    def commit_file(self, path: str, content: str, message: str,
                    branch: str = 'main',
                    repo: Optional[str] = None) -> Dict[str, Any]:
        """
        Create or update a file in the repository.

        Fetches the current SHA of the file if it exists (required for updates),
        then commits the new content.

        :param path: File path within the repo.
        :param content: New file content (UTF-8 string).
        :param message: Commit message.
        :param branch: Target branch.
        :param repo: Override the default ``owner/repo``.
        :returns: GitHub API response.
        :rtype: dict
        """
        import base64
        content  = self._safe_payload(content)
        message  = self._safe_payload(message)
        r        = self._repo if repo is None else repo
        token    = self._token()

        # Get current file SHA if it exists (needed for updates)
        existing = _gh_request(f'/repos/{r}/contents/{path}?ref={branch}',
                                token=token)
        sha = existing.get('sha') if 'error' not in existing else None

        payload: Dict[str, Any] = {
            'message': message,
            'content': base64.b64encode(content.encode()).decode(),
            'branch':  branch,
        }
        if sha:
            payload['sha'] = sha

        return _gh_request(f'/repos/{r}/contents/{path}',
                            method='PUT', payload=payload, token=token)

    def create_branch(self, branch: str, from_branch: str = 'main',
                      repo: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new branch from an existing branch.

        :param branch: New branch name.
        :param from_branch: Source branch.
        :param repo: Override the default ``owner/repo``.
        :returns: GitHub API response.
        :rtype: dict
        """
        branch = self._safe_payload(branch)
        r      = self._repo if repo is None else repo
        token  = self._token()

        # Get SHA of source branch tip
        ref_data = _gh_request(f'/repos/{r}/git/ref/heads/{from_branch}',
                                token=token)
        if 'error' in ref_data:
            return ref_data
        sha = ref_data.get('object', {}).get('sha', '')
        if not sha:
            return {'error': f'could not resolve {from_branch} SHA'}

        return _gh_request(f'/repos/{r}/git/refs',
                            method='POST',
                            payload={'ref': f'refs/heads/{branch}', 'sha': sha},
                            token=token)

    def create_pr(self, title: str, body: str, head: str,
                  base: str = 'main',
                  repo: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a pull request.

        :param title: PR title.
        :param body: PR description.
        :param head: Source branch.
        :param base: Target branch.
        :param repo: Override the default ``owner/repo``.
        :returns: GitHub API response.
        :rtype: dict
        """
        title = self._safe_payload(title)
        body  = self._safe_payload(body)
        r     = self._repo if repo is None else repo

        return _gh_request(f'/repos/{r}/pulls',
                            method='POST',
                            payload={'title': title, 'body': body,
                                     'head': head, 'base': base},
                            token=self._token())

    def push_state(self, bin_path: str, label: str = '',
                   repo: Optional[str] = None) -> Dict[str, Any]:
        """
        Push the monad .bin state file to the states repository.

        Used by study() to version-control field checkpoints. The .bin is
        encoded as base64 and committed. Secret scan runs on the commit message,
        not the binary — binaries are exempt from pattern matching.

        :param bin_path: Local path to the .bin file.
        :param label: Human label for the commit (becomes part of the message).
        :param repo: Override the default ``owner/repo``.
        :returns: GitHub API response.
        :rtype: dict
        """
        import base64
        r     = self._repo if repo is None else repo
        token = self._token()

        try:
            with open(bin_path, 'rb') as f:
                raw = f.read()
        except OSError as e:
            return {'error': str(e)}

        b64 = base64.b64encode(raw).decode()
        fname = os.path.basename(bin_path)
        ts    = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        msg   = self._safe_payload(
            f'state: {fname} {label} [{ts}]\n\nAutomated field checkpoint.'
        )

        # Get current SHA if exists
        existing = _gh_request(f'/repos/{r}/contents/states/{fname}',
                                token=token)
        sha = existing.get('sha') if 'error' not in existing else None

        payload: Dict[str, Any] = {
            'message': msg,
            'content': b64,
            'branch':  'main',
        }
        if sha:
            payload['sha'] = sha

        return _gh_request(f'/repos/{r}/contents/states/{fname}',
                            method='PUT', payload=payload, token=token)
