# Test Automation — README ![version](https://img.shields.io/badge/version-v0.4.0-blue)

## Visão geral
Este repo contém automações de:

- **WEB (Selenium)**
- **MOBILE (Appium)**
- **API (requests + pytest)**

Com:

- Page Objects (`pages/pages_web`, `pages/pages_mobile`)
- Organização de testes por plataforma/tipo:
  - `tests/tests_web`
  - `tests/tests_mobile`
  - `tests/tests_api`
- Relatórios e artefatos em `tests_compiled_info/<timestamp>_<suite>/`
- Parametrizações de execução via **pytest**, variáveis de ambiente e marcas de teste

---

## Estrutura

    pages/
      pages_mobile/
      pages_web/

    tests/
      tests_mobile/
      tests_web/
      tests_api/

    tests_compiled_info/   # saídas (dashboard, logs, screenshots, vídeos)

    utils/
      logger.py
      reporting.py

    data/
      testing.json

    pytest.ini

---

## Flags rápidas (em `conftest.py`)

- `OPEN_DASHBOARD` — abre o dashboard HTML ao final (default: `False`)
- `SAVE_ARTIFACTS` — salva screenshots/vídeos **apenas quando o teste falha** (default: `False`)
- `SAVE_EXEC_LOGS` — grava logs em arquivo (session/test) em vez de só console (default: `False`)

**Onde salva:**  
`tests_compiled_info/<YYYY-MM-DD_HH-MM-SS>_<suite>/`

A *suite* é definida via `--suite` ou deduzida pelo caminho dos testes:

- `--suite=web|mobile|api`
- Se rodar `pytest tests/tests_web ...`    → `web`
- Se rodar `pytest tests/tests_mobile ...` → `mobile`
- Se rodar `pytest tests/tests_api ...`    → `api`
- Caso contrário → `mixed`

---

## CLI (pytest)

Opções suportadas:

- `--suite=web|mobile|api` — sufixo no diretório da sessão
- `--notif=allow|block|ask` — controle de permissões de **notificações** do navegador (default: `allow`)

Exemplos:

    # Web
    pytest tests/tests_web    --suite=web    --notif=allow  -q
    pytest tests/tests_web    --suite=web    --notif=block  -q

    # Mobile
    pytest tests/tests_mobile --suite=mobile                -q

    # API
    pytest tests/tests_api    --suite=api    -m api         -q

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

### WEB — `browser` (Selenium)

- Abre Chrome/Firefox conforme `BROWSER`
- Aplica política de notificações conforme `--notif`
- Em **falha** e `SAVE_ARTIFACTS=True`: salva screenshot por teste

### MOBILE — `driver` (Appium)

- Android / UiAutomator2
- `appium:autoGrantPermissions=True`
- Em **falha** e `SAVE_ARTIFACTS=True`: grava e salva **vídeo** do teste (MP4)

### API

Principais fixtures e helpers de apoio para os testes de API:

- `base_api_url`  
  - Base da API local (ex.: `http://127.0.0.1:8000`).
- `api_client`  
  - Cliente HTTP baseado em `requests`.
- `json_data`  
  - Carrega dados de teste a partir de `data/testing.json`.
- `cleanup_users`  
  - Faz teardown por teste:
    - limpa produtos e wishlists do usuário autenticado
    - remove o próprio usuário (`DELETE /users/me`), usando o token salvo em `api_client.last_token`.

Helpers (definidos nos módulos de teste de API):

- `get_token_from_new_user(...)`  
  Cria um usuário único, faz login e retorna o token Bearer.
- `create_default_wishlist(...)`  
  Cria uma wishlist padrão para o usuário autenticado e retorna o `wishlist_id`.
- `add_four_products_on_wishlist(...)`  
  Adiciona 4 produtos em uma wishlist específica e retorna os objetos de produto (JSON) criados.

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

- `@pytest.mark.web`    — testes WEB  
- `@pytest.mark.mobile` — testes MOBILE  
- `@pytest.mark.api`    — testes de API

Filtragem:

    pytest -m web
    pytest -m mobile
    pytest -m api

---

## Execução — exemplos

    # Web (Chrome), permitir notificações
    BROWSER=chrome  pytest tests/tests_web    --suite=web    --notif=allow -q

    # Web (Firefox), bloquear notificações
    BROWSER=firefox pytest tests/tests_web    --suite=web    --notif=block -q

    # Mobile (Appium/Android)
    pytest          tests/tests_mobile --suite=mobile -q

    # API (Auth + Wishlists + Products)
    pytest tests/tests_api --suite=api -m api -q

---

## Progress Log

**2025-11-05**  
**Tag:** `v0.4.0`  

✅ **API – Cenários 8 a 36 finalizados (Auth, Wishlists, Products):**  

- **Auth (`/auth/register`, `/auth/login`)**
  - Cenários de sucesso, e-mail já registrado, dados inválidos
- **Wishlists (`/wishlists`, `/wishlists/{id}`)**
  - Criação com nome único
  - Erro para nome duplicado
  - Validações de dados obrigatórios
  - Recuperação de wishlists (lista vazia vs com itens)
  - Acesso não autenticado retornando `401`
- **Products (`/wishlists/{id}/products`, `/products/{id}`)**
  - Criação de produtos atrelados a wishlist
  - Filtros por `Product` (nome) e `is_purchased`
  - Update de produto (`PUT /products/{id}`)
  - Delete de produto (`DELETE /products/{id}`)
- **Endpoints protegidos**
  - Acesso sem token → `401 Unauthorized`
  - Acesso com token inválido (`Bearer invalidtoken`) → `401 Unauthorized`

> Arquivos:  
> `tests/tests_api/test_08-13_authentication_endpoints.py`  
> `tests/tests_api/test_14-20_wishlist_endpoints.py`  
> `tests/tests_api/test_21-34_product_endpoints.py`  
> `tests/tests_api/test_35-36_authenticated_endpoints.py`  
> Suíte: `--suite=api`, marca: `@pytest.mark.api`  

---

**2025-10-30**  
**Tag:** `v0.3.0`  

**Process note:** estes cenários foram commitados diretamente na `main` por engano. Mantive como baseline com a tag `v0.3.0`. A partir de agora: branch por cenário + PR com **squash & merge**.

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

## Convenções de Git (Git Flow leve)

1. **Branch por cenário ou bloco de cenários**  
   - Ex.: `feature/scenario-06-web`, `feature/api-scenarios-08-36`

2. **Commits com Conventional Commits**  

   Exemplos:

   - `feat(web): scenario 6 (password login) - happy path`  
   - `feat(api): add scenarios 08-36 for auth, wishlists and products`  
   - `test(api): adjust filters for is_purchased`  
   - `refactor(web): robust click in BasePage.click()`  
   - `docs(readme): bump v0.4.0 + progress log`  

3. **PRs pequenos e objetivos**  

   - Origem: `feature/...` → Destino: `main`  
   - **Squash & Merge** (1 commit limpinho por funcionalidade/bloco de cenários)  
   - Título do PR:  
     - `feat(api): cenários 8–36 – auth, wishlists e products`  
   - Descrição: passos do cenário + endpoints tocados + riscos/regressões

4. **Tags semânticas**  

   Após merge:

       git tag v0.4.0
       git push origin v0.4.0
