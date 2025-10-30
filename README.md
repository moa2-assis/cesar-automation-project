# Test Automation — README ![version](https://img.shields.io/badge/version-v0.3.0-blue)

## Visão geral
Este repo contém automações **WEB (Selenium)** e **MOBILE (Appium)** com:
- Page Objects (`pages/pages_web`, `pages/pages_mobile`)
- Organização de testes por plataforma (`tests/tests_web`, `tests/tests_mobile`)
- Relatórios e artefatos em `tests_compiled_info/<timestamp>_<suite>/`
- Parametrizações de execução via **pytest** e variáveis de ambiente

---

## Estrutura
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
    data/
      testing.json

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
    pytest tests/tests_web    --suite=web    --notif=allow  -q
    pytest tests/tests_mobile --suite=mobile                 -q

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
    BROWSER=chrome  pytest tests/tests_web --suite=web --notif=allow  -q
    BROWSER=firefox pytest tests/tests_web --suite=web --notif=block  -q

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
- `@pytest.mark.api_test` — testes de API

Filtragem:
    pytest -m web
    pytest -m mobile
    pytest -m api_test

---

## Execução — exemplos
    # Web (Chrome), permitir notificações
    BROWSER=chrome  pytest tests/tests_web    --suite=web    --notif=allow -q

    # Web (Firefox), bloquear notificações
    BROWSER=firefox pytest tests/tests_web    --suite=web    --notif=block -q

    # Mobile (Appium/Android)
    pytest          tests/tests_mobile --suite=mobile -q

---

## Progress Log

**2025-10-30**  
✅ **Web – Cenário 6 finalizado (Login com e-mail + senha válidos):**  
- Localizadores robustos para campos **e-mail** e **senha**  
- Botão “Entrar com email e senha” via XPath resiliente  
- Verificação de **home** usando elemento único da página inicial (banner topo) + presença do campo de busca

✅ **Web – Cenário 7 finalizado (Erro de login – credenciais inválidas):**  
- Validação do **alert de erro** `role="alert"` com `contains(.)` no texto  
- Garantias contra variações de layout (texto fragmentado)  
- Tratamento de clique robusto no botão de submit

> Arquivos (exemplos): `tests/tests_web/test_6_web.py`, `tests/tests_web/test_7_web.py`  
> POs envolvidos: `WebHomePage`, `WebLoginPage`, `WebAccountPage`
> Dados: `data/testing.json`

---

**2025-10-27**  
✅ **Web – Cenário 1 finalizado (Cadastro + Definir Senha):**  
- Cadastro de usuário **novo** com **temp-mail**  
- Captura/uso de **token de acesso**  
- Fluxo **Autenticação → Definir senha**  
  - Regras de senha via `data/testing.json`  
  - Invalidações deixam **Salvar senha** desabilitado  
  - Senha válida habilita salvar  
- Confirmação da **máscara de senha** no fim

> Arquivo: `tests/tests_web/test_1_web.py`  
> POs: `WebHomePage`, `WebLoginPage`, `WebTempMailPage`, `WebAccountPage`  
> Dados: `data/testing.json`

---

**2025-10-24**  
- Estrutura inicial do repo, flags de sessão, dashboard e integração base do Mobile/Web.

---

## Convenções de Git (Git Flow leve — “um cenário por branch”)

1) **Branch por cenário**  
- Nome: `feature/scenario-XX-web` (ou `-api`, `-mobile` quando chegar a hora)

2) **Commits com Conventional Commits**  
- `feat(web): scenario 6 (password login) - happy path`  
- `test(web): validate login error (scenario 7)`  
- `refactor(web): robust click in BasePage.click()`  
- `docs(readme): bump v0.3.0 + progress log`

3) **PRs pequenos e objetivos**  
- Origem: `feature/scenario-XX-web` → Destino: `main`  
- **Squash & Merge** (1 commit limpinho por cenário)  
- Título do PR: `feat(web): cenário 6 – login por senha`  
- Descrição: passos do cenário + páginas tocadas + riscos/regressões

4) **Tags semânticas**  
- Após merge:
    git tag v0.3.0
    git push origin v0.3.0
