---
plan_id: "006"
title: "agent-explorer-webview"
status: pending
agent: claude
created_at: "2026-05-03T00:00:00Z"
updated_at: "2026-05-03T00:00:00Z"
---

# Plan: Agent Explorer — WebviewView

## Objetivo

Implementar a interface visual completa: HTML/CSS/JS do webview, sistema de mensagens
extension↔webview, e o `WebviewViewProvider` que os conecta.

Referência de design: `plan-002`.

---

## `webview/html/style.css`

CSS puro usando exclusivamente `var(--vscode-*)`. Sem frameworks externos.

Seções do arquivo:
```
/* Reset */
/* Body / layout */
/* Search bar */
/* Platform chips */
/* Section (details/summary) */
/* Card */
/* Kind icons */
/* Platform badges */
/* States: loading, empty, no-results, error */
/* Spinner animation */
/* Scrollbar */
```

---

## `webview/html/template.ts`

Exporta função que recebe `ScanResult + nonce + kindIconUris` e retorna HTML string completo.

```typescript
export function buildTemplate(options: {
  result: ScanResult;
  nonce: string;
  kindIcons: Record<ArtifactKind, string>;
  installedPlatforms: PlatformId[];
  defaultExpandedKinds: ArtifactKind[];
}): string
```

**Estrutura do HTML gerado:**
```html
<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="Content-Security-Policy" content="...nonce...">
  <style>/* style.css injetado inline */</style>
</head>
<body data-state="ready">

  <div class="search-container">
    <input type="search" id="search" placeholder="Search artifacts…" />
  </div>

  <div class="chips" role="group" aria-label="Filter by platform">
    <button class="chip active" data-platform="all">All</button>
    <!-- uma chip por plataforma detectada -->
  </div>

  <!-- Sections por kind (KIND_ORDER) -->
  <details class="section" data-kind="warrior">
    <summary class="section-header">
      <span class="section-label">Warriors</span>
      <span class="section-count" aria-live="polite">14</span>
    </summary>
    <div class="cards">
      <div class="card" role="button" tabindex="0"
           data-file-path="..." data-platforms="ahrena claude"
           data-name="warrior-prometheus" data-desc="...">
        <span class="kind-icon"><!-- SVG inline --></span>
        <div class="card-body">
          <span class="card-name">warrior-prometheus</span>
          <span class="card-desc">Technical Product Manager…</span>
          <div class="badges">
            <span class="badge badge-ahrena">Ahrena</span>
          </div>
        </div>
      </div>
    </div>
  </details>

  <div class="state-empty" hidden>…</div>
  <div class="state-no-results" hidden>…</div>

  <script nonce="...">/* JS de filtro inline */</script>
</body>
</html>
```

---

## JS client-side (inline, com nonce)

```javascript
(function() {
  const vscode = acquireVsCodeApi();

  // Abertura de arquivo
  document.addEventListener('click', (e) => {
    const card = e.target.closest('[role="button"]');
    if (!card) return;
    vscode.postMessage({
      type: 'openArtifact',
      filePath: card.dataset.filePath,
      lineNumber: card.dataset.lineNumber ? +card.dataset.lineNumber : undefined,
    });
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.target.closest('[role="button"]')?.click();
    }
  });

  // Platform filter
  let activePlatform = 'all';
  document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => {
      activePlatform = chip.dataset.platform === activePlatform
        ? 'all' : chip.dataset.platform;
      applyFilters();
    });
  });

  // Search filter
  document.getElementById('search').addEventListener('input', applyFilters);

  function applyFilters() {
    const query = document.getElementById('search').value.toLowerCase().trim();

    document.querySelectorAll('.chip').forEach(c =>
      c.classList.toggle('active',
        c.dataset.platform === activePlatform ||
        (activePlatform === 'all' && c.dataset.platform === 'all')));

    let totalVisible = 0;
    document.querySelectorAll('.card').forEach(card => {
      const matchesPlatform = activePlatform === 'all' ||
        card.dataset.platforms.split(' ').includes(activePlatform);
      const matchesQuery = !query ||
        card.dataset.name.includes(query) || card.dataset.desc.includes(query);
      const visible = matchesPlatform && matchesQuery;
      card.classList.toggle('hidden', !visible);
      if (visible) totalVisible++;
    });

    document.querySelectorAll('.section').forEach(section => {
      const n = section.querySelectorAll('.card:not(.hidden)').length;
      section.querySelector('.section-count').textContent = n;
      section.classList.toggle('section--empty', n === 0);
    });

    const noResults = totalVisible === 0 && (query || activePlatform !== 'all');
    document.querySelector('.state-no-results').hidden = !noResults;
    document.querySelector('.state-empty').hidden = totalVisible > 0 || noResults;
  }

  window.addEventListener('message', (e) => {
    if (e.data.type === 'loading') document.body.dataset.state = 'loading';
  });

  vscode.postMessage({ type: 'ready' });
})();
```

---

## `webview/html/build-html.ts`

```typescript
export function buildHtml(options: {
  webview: vscode.Webview;
  extensionUri: vscode.Uri;
  result: ScanResult;
  defaultExpandedKinds: ArtifactKind[];
}): string
```

Responsabilidades:
- Gera `nonce = crypto.randomBytes(16).toString('hex')`
- Resolve URIs dos SVGs via `webview.asWebviewUri()`
- Lê `style.css` do disco e injeta inline
- Chama `buildTemplate(...)` e retorna HTML final

---

## `webview/message-handler.ts`

| Mensagem recebida | Ação |
|-------------------|------|
| `{ type: 'ready' }` | noop |
| `{ type: 'openArtifact', filePath, lineNumber }` | `openTextDocument` + `showTextDocument` + `revealRange` |

---

## `webview/explorer-view-provider.ts` (atualização do stub)

```
resolveWebviewView():
  1. seta options (enableScripts, localResourceRoots)
  2. seta HTML de loading
  3. registra listener de mensagens → handleWebviewMessage
  4. inicia scanner e watcher
  5. scan() → webview.html = buildHtml(result)

refresh():
  postMessage({ type: 'loading' })
  scan() → webview.html = buildHtml(result)
```

---

## Steps

- [ ] 1. Criar `src/webview/html/style.css`
- [ ] 2. Criar `src/webview/html/template.ts`
- [ ] 3. Criar `src/webview/html/build-html.ts`
- [ ] 4. Criar `src/webview/message-handler.ts`
- [ ] 5. Atualizar `src/webview/explorer-view-provider.ts` (integrar scanner + build-html)
- [ ] 6. Criar SVGs dos kind icons em `media/icons/`
- [ ] 7. Testar no Extension Development Host com workspace do ahrena

## Dependências

- `plan-002` (spec de UI)
- `plan-005` (scanner + watcher prontos)
- `plan-001` (tipos)
