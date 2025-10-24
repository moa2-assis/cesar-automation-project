# Test Automation — README

## Visão geral
Este repo contém automações **WEB (Selenium)** e **MOBILE (Appium)** com:
- Page Objects (`pages/pages_web`, `pages/pages_mobile`)
- Organização de testes por plataforma (`tests/tests_web`, `tests/tests_mobile`)
- Relatórios e artefatos em `tests_compiled_info/<timestamp>_<suite>/`
- Parametrizações de execução via **pytest** e variáveis de ambiente

---

## Estrutura
```
pages/
  pages_mobile/
  pages_web/
tests/
  tests_mobile/
  tests_web/
tests_compiled_info/   # saídas (dashboard, logs, screenshots, vídeos)
utils/
  logger.py
  reporting.py
```

---

## Flags rápidas (em `conftest.py`)
- `OPEN_DASHBOARD` — abre o dashboard HTML ao final (default: `False`)
- `SAVE_ARTIFACTS` — salva screenshots/vídeos **apenas quando o teste falha** (default: `False`)
- `SAVE_EXEC_LOGS` — grava logs em arquivo (session/test) em vez de só console (default: `False`)

**Onde salva:**  
`tests_compiled_info/<YYYY-MM-DD_HH-MM-SS>_<suite>/`

A *suite* é definida via `--suite` ou deduzida pelo caminho dos testes:
- `--suite=web|mobile`  
- Se rodar `pytest tests/tests_web ...` → `web`  
- Se rodar `pytest tests/tests_mobile ...` → `mobile`  
- Caso contrário → `mixed`

---

## CLI (pytest)
Opções suportadas:
- `--suite=web|mobile` — sufixo no diretório da sessão
- `--notif=allow|block|ask` — controle de permissões de **notificações** do navegador (default: `allow`)

Exemplos:
```bash
pytest tests/tests_web    --suite=web    --notif=allow  -q
pytest tests/tests_mobile --suite=mobile                 -q
```

---

## Seleção de navegador (Web)
Use a variável de ambiente `BROWSER`:
- `BROWSER=chrome` (default)
- `BROWSER=firefox`

**Chrome:** `profile.default_content_setting_values.notifications` (1=allow, 2=block, 0=ask)  
**Firefox:** profile com:
- `permissions.default.desktop-notification`
- `permissions.default.geo`
- `permissions.default.camera`
- `permissions.default.microphone`
- `dom.webnotifications.enabled`, `dom.push.enabled`

Exemplos:
```bash
BROWSER=chrome  pytest tests/tests_web --suite=web --notif=allow  -q
BROWSER=firefox pytest tests/tests_web --suite=web --notif=block  -q
```

---

## Fixtures principais

### `browser` (WEB / Selenium)
- Abre Chrome/Firefox conforme `BROWSER`
- Aplica política de notificações conforme `--notif`
- Em **falha** e `SAVE_ARTIFACTS=True`: salva screenshot por teste

### `driver` (MOBILE / Appium)
- Android / UiAutomator2
- `appium:autoGrantPermissions=True`
- Em **falha** e `SAVE_ARTIFACTS=True`: grava e salva **vídeo** do teste (MP4)

---

## Artefatos & Logs
- **Artefatos (screenshots/vídeos):** somente **em falhas** e quando `SAVE_ARTIFACTS=True`
- **Logs:**
  - `SAVE_EXEC_LOGS=True` → grava `session_log.txt` + `test_log.txt`
  - `False` → log apenas no console
- **Dashboard:** sempre gerado em `<sessão>/dashboard.html`  
  - Abre automaticamente se `OPEN_DASHBOARD=True`

---

## Marcas de teste
- `@pytest.mark.web` — testes WEB  
- `@pytest.mark.mobile` — testes MOBILE

Filtragem:
```bash
pytest -m web
pytest -m mobile
```

---

## Page Objects (resumo)

### Base genérica (`BasePage`)
- Wait helpers: `find_element`, `wait_for_visibility`, `wait_clickable`
- Ações: `click`, `type`, `get_text`, `is_visible`, `attr`

### WEB (`WebBasePage`)
- `open(url)`
- `js_click(by, locator)`
- `scroll_into_view(by, locator, block='center')`
- `switch_to_tab(index)`

### Web — casos práticos já implementados
- **Fechar banner** Insider: `HomeWeb.close_banner_if_present()`  
  Busca `div[id^='ins-responsive-banner-']` e tenta clicar no “X” (wrapper/botão/svg), com fallback JS.
- **Login link**: locator por classe **prefixada** (`ButtonLogin_Container__`) + `href^='/login'`  
  `HomeWeb.click_login_link()` usa `element_to_be_clickable` + fallback JS click.

### Temp Mail (Web)
- `WebTempMailPage.open_temp_mail_in_new_tab()` — abre **em nova aba** e guarda handles
- `get_temp_email_value(timeout=20)` — espera `#email` com `value` contendo `@`
- `switch_to_temp_tab()` / `switch_to_main_tab()` — alterna abas
- `click_refresh_button()` — clica no `div.refresh`
- `get_access_code_burraço()` — procura assunto com “código de acesso” e extrai **6 dígitos** (últimos)

---

## Execução — exemplos
```bash
# Web (Chrome), permitir notificações
BROWSER=chrome  pytest tests/tests_web    --suite=web    --notif=allow -q

# Web (Firefox), bloquear notificações
BROWSER=firefox pytest tests/tests_web    --suite=web    --notif=block -q

# Mobile (Appium/Android)
pytest          tests/tests_mobile --suite=mobile -q
```

---

## Git — “um cenário por branch”
- Começar cenário:
  ```bash
  git switch main && git pull
  git switch -c feature/scenario-01-web
  ```
- Trabalhar/commit/push:
  ```bash
  git add -A
  git commit -m "feat(web): cenário 1 steps 1–6"
  git push -u origin feature/scenario-01-web
  ```
- **PR:** `feature/scenario-01-web` → `main` (Squash & Merge)
- Próximo cenário sempre nasce da `main` atualizada.

---

## Progress Log (tipo changelog)

**2025-10-24**
- **Repo/estrutura inicial:** `pages_*`, `tests_*`, `tests_compiled_info/`, utils (`logger`, `reporting`)
- **Parametrização do `conftest.py`:**
  - Flags: `OPEN_DASHBOARD`, `SAVE_ARTIFACTS`, `SAVE_EXEC_LOGS`
  - CLI: `--suite`, `--notif`
  - Sessão: `tests_compiled_info/<timestamp>_<suite>/`
- **Mobile base:** Appium Android sobe app, vídeo em falhas quando habilitado
- **Web – Cenário 1 (steps 1–6):**
  - Acessa Americanas
  - Fecha banner Insider (selector escopado + fallback JS)
  - Clica link de login (classe prefixada + `href^='/login'`)
  - Abre Temp Mail em **nova aba**
  - Captura e-mail (`#email` com `value` != vazio, contendo `@`)
  - Alterna abas (temp ↔ main) e preenche fluxo de login (submit e-mail)
- **Git flow (adotado a partir de hoje):**
  - 1 branch por cenário → PR → `main`
  - `feature/scenario-01-web` para continuar os próximos passos