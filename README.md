# Test Automation — README ![version](https://img.shields.io/badge/version-v0.2.0-blue)

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

## Progress Log

**2025-10-27**
✅ **Web – Cenário 1 finalizado (Login + Definir Senha):**
- Cadastro de usuário **novo e aleatório** usando temp-mail
- Captura e uso de **token de acesso** em tempo real
- Fluxo de **Autenticação > Definir senha**
  - Validação de regras de senha (JSON `testing.json`)
  - Senhas inválidas → botão **desabilitado**
  - Senha válida → botão **habilitado**
- Verificação final:
  - Máscara de senha (************) exibida corretamente
- Teste estável e **100% automatizado** do início ao fim ✅

> 🔹 Arquivo principal: `tests/tests_web/test_1_web.py`  
> 🔹 Page Objects envolvidos: `WebHomePage`, `WebLoginPage`, `WebTempMailPage`, `WebAccountPage`  
> 🔹 Dados externos: `data/testing.json`

---

**2025-10-24**
- **Repo/estrutura inicial:** `pages_*`, `tests_*`, `tests_compiled_info/`, utils (`logger`, `reporting`)
- **Parametrização do `conftest.py`:**
  - Flags: `OPEN_DASHBOARD`, `SAVE_ARTIFACTS`, `SAVE_EXEC_LOGS`
  - CLI: `--suite`, `--notif`
  - Sessão: `tests_compiled_info/<timestamp>_<suite>/`
- **Mobile base:** Appium Android sobe app, vídeo em falhas quando habilitado
- **Web – Cenário 1 (steps 1–6 iniciais):**
  - Acessa Americanas
  - Fecha banner Insider (selector escopado + fallback JS)
  - Clica link de login
  - Abre Temp Mail em nova aba
  - Captura e-mail temporário
  - Alterna abas e preenche fluxo inicial de login
- **Git flow** (Squash & Merge por cenário)
