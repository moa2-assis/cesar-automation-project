# Test Automation — README ![version](https://img.shields.io/badge/version-v0.5.0-blue)

## Visão geral
Este repo contém automações:

- **WEB (Selenium)**
- **MOBILE (Appium)**
- **API (requests + pytest)**

Com:

- Page Objects (`pages/pages_web`, `pages/pages_mobile`)
- Organização de testes por plataforma (`tests/tests_web`, `tests/tests_mobile`, `tests/tests_api`)
- Relatórios e artefatos em `tests_compiled_info/<timestamp>_<suite>/`
- Parametrizações de execução via **pytest** e variáveis de ambiente

---

## Estrutura

```text
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
  api_reader.py       # helpers para consumir a API do desafio
data/
  testing.json        # dados de usuário/wishlist/produtos (API + Web)
pytest.ini
conftest.py
README.md
```

---

## Flags rápidas (em `conftest.py`)

```python
OPEN_DASHBOARD = False   # abre o dashboard HTML ao final
SAVE_ARTIFACTS = False   # salva screenshots/vídeos quando o teste falha
SAVE_EXEC_LOGS = False   # grava logs em arquivo (session/test) ou só console
```

Saída:

```text
tests_compiled_info/<YYYY-MM-DD_HH-MM-SS>_<suite>/
```

A *suite* é definida via `--suite` ou deduzida pelo caminho dos testes:

- `--suite=web|mobile|api`
- Se rodar `pytest tests/tests_web ...`   → `web`
- Se rodar `pytest tests/tests_mobile ...` → `mobile`
- Se rodar `pytest tests/tests_api ...`   → `api`
- Caso contrário → `mixed`

---

## CLI (pytest)

Opções suportadas:

- `--suite=web|mobile|api` — sufixo no diretório da sessão
- `--notif=allow|block|ask` — controle de permissões de **notificações** do navegador (default: `allow`, só para WEB)

Exemplos:

```bash
# Web
pytest tests/tests_web    --suite=web    --notif=allow  -q

# Mobile
pytest tests/tests_mobile --suite=mobile                -q

# API
pytest tests/tests_api    --suite=api                   -q
```

---

## Seleção de navegador (Web)

Use a variável de ambiente `BROWSER`:

- `BROWSER=chrome`  (default)
- `BROWSER=firefox`

Chrome:

- Usa preferências em `profile.default_content_setting_values.notifications` (1=allow, 2=block, 0=ask)

Firefox:

- Preferências usadas:
  - `permissions.default.desktop-notification`
  - `permissions.default.geo`
  - `permissions.default.camera`
  - `permissions.default.microphone`
  - `dom.webnotifications.enabled`
  - `dom.push.enabled`

Exemplos:

```bash
BROWSER=chrome  pytest tests/tests_web --suite=web --notif=allow  -q
BROWSER=firefox pytest tests/tests_web --suite=web --notif=block  -q
```

---

## Fixtures principais

### Web: `browser` (Selenium)

- Abre Chrome/Firefox conforme `BROWSER`
- Aplica política de notificações conforme `--notif`
- Em **falha** e `SAVE_ARTIFACTS=True`: salva **screenshot** por teste  
- Integrado ao dashboard em `tests_compiled_info/.../dashboard.html`

Uso:

```python
def test_exemplo_web(browser):
    browser.get("https://www.americanas.com.br")
```

---

### Mobile: `driver` (Appium / Android)

Configuração básica (em `conftest.py`):

- `platformName: Android`
- `automationName: UiAutomator2`
- `appium:autoGrantPermissions=True`
- `appium:appWaitActivity`, `appium:appWaitDuration` etc.

Comportamento:

- Em **falha** e `SAVE_ARTIFACTS=True`: grava **vídeo** da execução e salva como `.mp4`
- Sempre fecha a sessão do Appium no teardown

Uso:

```python
def test_exemplo_mobile(driver):
    # exemplo: conferir activity inicial, elemento de home, etc.
    assert driver.current_package == "com.b2w.americanas"
```

---

### API: fixtures auxiliares

Definidas em `conftest.py`:

```python
@pytest.fixture(scope="session")
def base_api_url():
    return "http://127.0.0.1:8000"

@pytest.fixture(scope="function")
def api_client():
    return requests

@pytest.fixture(scope="session")
def json_data(pytestconfig):
    # carrega data/testing.json
```

Fixtures de limpeza específicas dos recursos da API:

- `cleanup_users`
- `cleanup_wishlists`
- `cleanup_products`

Uso típico:

```python
@pytest.mark.api
def test_alguma_coisa(api_client, base_api_url, cleanup_users):
    # cria usuário / wishlist / products
    # ao final do teste, cleanup_users tenta limpar usuários criados para não “sujar” o banco
```

> As fixtures de cleanup são **best-effort**: se não houver nada para limpar, não causam falha.

---

## Artefatos & Logs

- **Artefatos (screenshots/vídeos):**
  - Somente em **falhas**
  - Apenas quando `SAVE_ARTIFACTS=True`
  - Salvos dentro da pasta de cada teste:  
    `tests_compiled_info/<sessão>/<NNN_nome_DO_TESTE_STATUS>/`

- **Logs:**
  - `SAVE_EXEC_LOGS=True` → grava:
    - `session_log.txt` (nível de sessão)
    - `test_log.txt` por teste
  - `SAVE_EXEC_LOGS=False` → logs apenas no console

- **Dashboard:**
  - Sempre gerado em `<sessão>/dashboard.html`
  - Abre automaticamente se `OPEN_DASHBOARD=True`

---

## Marcas de teste

- `@pytest.mark.web`    — testes WEB  
- `@pytest.mark.mobile` — testes MOBILE  
- `@pytest.mark.api`    — testes de API

Filtragem:

```bash
pytest -m web
pytest -m mobile
pytest -m api
```

Com suite:

```bash
pytest tests/tests_web    -m web    --suite=web
pytest tests/tests_mobile -m mobile --suite=mobile
pytest tests/tests_api    -m api    --suite=api
```

---

## Execução — exemplos

### Web (Chrome + Firefox)

```bash
# Chrome, permitir notificações
BROWSER=chrome pytest tests/tests_web --suite=web --notif=allow

# Firefox, bloquear notificações
BROWSER=firefox pytest tests/tests_web --suite=web --notif=block
```

### Mobile (Appium/Android)

```bash
pytest tests/tests_mobile --suite=mobile
```

> Requer Appium Server rodando e emulador/dispositivo configurado (`emulator-5554` na config atual).

### API (Auth + Wishlists + Products)

```bash
# rodar todos os testes de API
pytest tests/tests_api --suite=api -m api

# rodar apenas auth (ex.: arquivos 08-13)
pytest tests/tests_api/test_08-13_authentication_endpoints.py --suite=api -m api

# rodar apenas wishlists/products
pytest tests/tests_api/test_14-20_wishlist_endpoints.py --suite=api -m api
pytest tests/tests_api/test_21-34_product_endpoints.py   --suite=api -m api
pytest tests/tests_api/test_35-36_authenticated_endpoints.py --suite=api -m api
```

---

## Cenários automatizados (resumo)

### Web

- **Cenário 1 – Cadastro + Definir senha**
  - Fluxo de cadastro via temp-mail + definição de senha.
- **Cenário 5 – Buscar e validar produto da Wishlist (API → Web)**  
  - Lê a wishlist `projeto_final` via API.
  - Para cada produto:
    - Pesquisa no site
    - Valida título e preço em **grid view**
    - Valida título e preço em **list view**
    - Abre página de produto e valida título e preço novamente.
- **Cenário 6 – Login com e-mail + senha válidos**
- **Cenário 7 – Erro de login (credenciais inválidas)**

### Mobile

- **Setup inicial + abertura do app na home** (Appium)  
  > Cenários 3, 5, 6, 7 ainda a espelhar dos cenários Web.

### API

**Auth (`/auth/register`, `/auth/login`) – Cenários 8–13**

- Registro de usuário bem-sucedido
- E-mail já existente
- Dados inválidos (validações 422)
- Login com credenciais válidas
- Login com senha incorreta
- Login com usuário inexistente

**Wishlists (`/wishlists`) – Cenários 14–20**

- Criar wishlist autenticado
- Impedir nome duplicado para o mesmo usuário
- Criar wishlist sem autenticação (401)
- Criar wishlist com dados inválidos (422)
- Listar wishlists de um usuário
- Listar retornando array vazio quando não há wishlists
- Impedir listar wishlists sem autenticação

**Products (`/wishlists/{id}/products`, `/products/{id}`) – Cenários 21–34**

- Adicionar produto a wishlist
- Impedir adicionar em wishlist inexistente
- Impedir adicionar em wishlist de outro usuário
- Validações de payload incompleto (422)
- Listar produtos de uma wishlist
- Filtro por nome (`Product=...`)
- Filtro por `is_purchased`
- Impedir visualizar produtos de wishlist de outro usuário
- Atualizar produto (`PUT /products/{id}`)
- Impedir atualizar produto inexistente ou de outro usuário
- Deletar produto (`DELETE /products/{id}`)
- Impedir deletar produto inexistente ou de outro usuário

**Endpoints autenticados – Cenários 35–36**

- Acessar endpoints protegidos **sem token** → 401
- Acessar endpoints protegidos com **token inválido** → 401

---

## Progress Log

**2025-11-05**  
**Tag prevista:** `v0.5.0`

✅ **API – Cenários 8–36 concluídos (Auth, Wishlists, Products, Auth-required):**

- Cobertura de:
  - `/auth/register`, `/auth/login`
  - `/wishlists`
  - `/wishlists/{wishlist_id}/products`
  - `/products/{product_id}`
  - `/products/{product_id}/toggle` (quando aplicável)
- Uso de fixtures de cleanup (`cleanup_users`, `cleanup_wishlists`, `cleanup_products`) para manter o banco consistente entre execuções.
- Helpers para:
  - criar usuário e obter token (`get_token_from_new_user`)
  - criar wishlist padrão
  - adicionar múltiplos produtos para cenários de listagem/filtro.

✅ **Web – Cenário 5 (buscar produto da wishlist via API e validar na UI):**

- Leitura da wishlist `projeto_final` via `utils/api_reader.py`:
  - Usuário default: `projeto@example.com` / `Senha123!`
  - Wishlist default: `projeto_final`
- Validação, por produto:
  - Pesquisa no site
  - Checagem de nome e preço em **grid view** e **list view**
  - Checagem de nome e preço na **página de produto**

---

**2025-10-30**  
**Tag:** `v0.3.0`  

✅ **Web – Cenário 6 (Login com e-mail + senha válidos):**

- Localizadores robustos para campos **e-mail** e **senha**
- Botão “Entrar com email e senha” via XPath resiliente
- Verificação de **home** usando elemento único da página inicial + campo de busca

✅ **Web – Cenário 7 (Erro de login – credenciais inválidas):**

- Validação do **alert de erro** `role="alert"` com `contains(.)` no texto
- Cuidado com variações de layout
- Tratamento de clique robusto no botão de submit

> Arquivos (exemplos):  
> `tests/tests_web/test_6_web.py`, `tests/tests_web/test_7_web.py`  
> POs: `WebHomePage`, `WebLoginPage`, `WebAccountPage`  
> Dados: `data/testing.json`

---

**2025-10-27**  

✅ **Web – Cenário 1 (Cadastro + Definir Senha):**

- Cadastro de usuário **novo** com **temp-mail**
- Captura/uso de token de acesso
- Fluxo **Autenticação → Definir senha**
  - Regras de senha via `data/testing.json`
  - Invalidações desabilitam botão **Salvar senha**
  - Senha válida habilita botão
- Confirmação da **máscara de senha** ao final

> Arquivo: `tests/tests_web/test_1_web.py`  
> POs: `WebHomePage`, `WebLoginPage`, `WebTempMailPage`, `WebAccountPage`  
> Dados: `data/testing.json`

---

**2025-10-24**  

- Estrutura inicial do repo, flags de sessão, dashboard e integração base Mobile/Web.

---

## Convenções de Git (Git Flow leve — “um cenário por branch”)

1. **Branch por cenário ou grupo de cenários**

   Exemplos:

   ```bash
   # Web
   feature/web-scenario-01-registration
   feature/web-scenario-05-wishlist-products
   feature/web-scenarios-06-07-login

   # API
   feature/api-scenarios-08-36
   ```

2. **Commits com Conventional Commits**

   Exemplos:

   ```text
   feat(api): scenarios 08-13 auth endpoints
   feat(api): scenarios 14-20 wishlists
   feat(api): scenarios 21-34 products
   feat(api): scenarios 35-36 auth required endpoints

   feat(web): scenario 5 (wishlist product validation)
   test(web): improve price normalization helper
   refactor(web): simplify WebBasePage click helper
   docs(readme): add api section and bump v0.4.0
   ```

3. **PRs pequenos e objetivos**

   - Origem: `feature/...` → Destino: `main`
   - **Squash & Merge** (1 commit limpo por cenário/grupo)
   - Título do PR:
     - `feat(api): scenarios 08-36 (auth, wishlists, products)`
     - `feat(web): scenario 5 – wishlist product validation`
   - Descrição:
     - Passos do cenário
     - Páginas/fixtures tocadas
     - Riscos/regressões possíveis

4. **Tags semânticas**

   Após merge na `main`:

   ```bash
   git tag v0.4.0
   git push origin v0.4.0
   ```

   (ou o próximo número de versão conforme evolução do projeto)

---