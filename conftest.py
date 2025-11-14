import base64
import json
import os
import selenium.webdriver as swd
import pytest
import requests

from pathlib import Path
from datetime import datetime
from typing import Optional

from appium import webdriver as appwd
from appium.options.common.base import AppiumOptions

from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FFOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from utils import reporting as R
from utils.logger import setup_logger

# novo: pytest -m "web or api" --suite=mixed --browser all

# antigo:
# git checkout bade3c19467ed3295341cbd8716ed4191639097d
# pytest tests/tests_web -m web --suite=web --browser all

# pytest tests/tests_web -m web --suite=web --browser chrome

# pytest tests/tests_web -m web --suite=web --browser firefox

# ==========================================================
# CONFIGURAÇÃO RÁPIDA
# ==========================================================
# Abre o dashboard HTML ao fim da execução, e se passar variável "export CI=true" pelo Jenkins, reescreve para nunca abrir automático
OPEN_DASHBOARD = True
if os.getenv("CI", "").lower() == "true":
    OPEN_DASHBOARD = False
# Salva screenshots/vídeos e quaisquer artefatos de erro
SAVE_ARTIFACTS = True
# Salva logs em arquivos (session_log.txt e test_log.txt)
SAVE_EXEC_LOGS = True
# ==========================================================

# ===== estado da sessão =====
LOG = None
SESSION_DIR: Optional[Path] = None
TEST_COUNTER = 0
NODEID_TO_TESTDIR = {}


# ==========================================================
# CLI options (para sufixo mobile/web/api e notificações do browser)
# ==========================================================
def pytest_addoption(parser):
    parser.addoption(
        "--suite",
        action="store",
        default=None,  # se None, vamos inferir por caminho passado
        help="Identificador da suíte: web | mobile | api | mixed (default: inferido pelos caminhos dos testes)",
    )
    parser.addoption(
        "--notif",
        action="store",
        default="allow",  # allow | block | ask
        help="Controle de notificações do navegador: allow | block | ask (default: allow)",
    )
    parser.addoption(
        "--browser",
        action="store",
        default=os.getenv("BROWSER", "chrome"),
        help="chrome | firefox | all (default: env BROWSER ou 'chrome')",
    )


# ===== helpers =====
def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _rel_to_session(p: Path) -> str:
    return str(p.relative_to(SESSION_DIR))


def _sanitize(name: str) -> str:
    bad = '\\/:*?"<>|'
    for ch in bad:
        name = name.replace(ch, "_")
    return name.strip() or "test"


def _write_test_log_line(test_dir: Path, msg: str) -> None:
    if not SAVE_EXEC_LOGS:
        return
    (test_dir / "test_log.txt").open("a", encoding="utf-8").write(
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n"
    )


def _build_console_logger():
    import logging

    logger = logging.getLogger("pytest-session")
    logger.setLevel(logging.INFO)
    logger.handlers = []
    ch = logging.StreamHandler()
    fmt = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    return logger


def _normalize_browsers(opt: str):
    opt = (opt or "").lower().strip()
    if opt in ("all", "both"):
        return ["chrome", "firefox"]
    if "," in opt:
        return [b.strip() for b in opt.split(",") if b.strip()]
    return [opt or "chrome"]


def _infer_suite_from_config(config) -> str:
    cli_suite = config.getoption("--suite")
    if cli_suite:
        return cli_suite.strip().lower()
    # fallback: deduz pelos args (igual você já faz)
    args = getattr(config, "args", []) or []
    joined = " ".join(str(a) for a in args).lower()
    if "tests_mobile" in joined:
        return "mobile"
    if "tests_web" in joined:
        return "web"
    if "tests_api" in joined:
        return "api"
    return "mixed"


def pytest_generate_tests(metafunc):
    """
    Se o teste usa a fixture 'browser' (Selenium), parametriza com os navegadores
    solicitados via --browser/BROWSER **apenas** quando a suíte for web/mixed.
    """
    if "browser" in metafunc.fixturenames:
        suite = _infer_suite_from_config(metafunc.config)
        if suite in ("web", "mixed"):
            opt = metafunc.config.getoption("--browser")
            browsers = _normalize_browsers(opt)
            metafunc.parametrize("browser", browsers, indirect=True, scope="function")


# ===== pytest lifecycle =====
@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    """Cria o 'paizinho' da sessão e inicializa o logger de sessão dentro dele."""
    global LOG, SESSION_DIR

    # 1) via CLI (--suite=mobile|web|api)
    cli_suite = session.config.getoption("--suite")
    if cli_suite:
        suite_name = cli_suite.strip().lower()
    else:
        # 2) deduz pelos paths passados (ex.: pytest tests/tests_mobile ...)
        args = getattr(session.config, "args", []) or []
        joined = " ".join(str(a) for a in args).lower()
        if "tests_mobile" in joined:
            suite_name = "mobile"
        elif "tests_web" in joined:
            suite_name = "web"
        elif "tests_api" in joined:
            suite_name = "api"
        else:
            suite_name = "mixed"

    timestamp = _timestamp()
    SESSION_DIR = Path("tests_compiled_info") / f"{timestamp}_{suite_name}"
    _ensure_dir(SESSION_DIR)

    # Logger: arquivo + console (SAVE_EXEC_LOGS=True) ou somente console (False)
    if SAVE_EXEC_LOGS:
        LOG = setup_logger(SESSION_DIR / "session_log.txt")
    else:
        LOG = _build_console_logger()

    LOG.info("=== Pytest session STARTED ===")
    LOG.info(f"Output dir: {SESSION_DIR}")
    LOG.info(f"Suite: {suite_name}")

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Gera dashboard e session_summary.json dentro do paizinho."""
    R.write_session_summary(SESSION_DIR, exitstatus)

    if OPEN_DASHBOARD:
        R.write_and_open_dashboard(SESSION_DIR)
        LOG.info("[DASHBOARD] auto-open enabled → abrindo no navegador...")
    else:
        R.write_dashboard(SESSION_DIR)
        LOG.info("[DASHBOARD] auto-open desativado → apenas gerado no diretório")

    LOG.info(f"=== Pytest session FINISHED (exitstatus={exitstatus}) ===")
    LOG.info(f"Dashboard: {SESSION_DIR / 'dashboard.html'}")
    if SAVE_EXEC_LOGS:
        LOG.info(f"Session log: {SESSION_DIR / 'session_log.txt'}")
    else:
        LOG.info("Session log: (não gravado em arquivo — SAVE_EXEC_LOGS=False)")


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """Numera os testes pela ordem REAL de execução."""
    global TEST_COUNTER
    TEST_COUNTER += 1
    item._exec_index = TEST_COUNTER
    LOG.info(f"=== START test {item._exec_index:03d}: {item.nodeid} ===")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Cria pasta do teste, registra resultado e artefatos (quando aplicável)."""
    outcome = yield
    rep = outcome.get_result()

    setattr(item, f"rep_{rep.when}", rep)

    should_create_dir = (rep.when == "call") or (rep.when == "setup" and rep.failed)
    if should_create_dir:
        outcome_upper = rep.outcome.upper()
        sanitized = _sanitize(item.name)
        test_dirname = f"{item._exec_index:03d}_{sanitized}_{outcome_upper}"
        test_dir = SESSION_DIR / test_dirname
        NODEID_TO_TESTDIR[item.nodeid] = test_dir
        _ensure_dir(test_dir)

        R.upsert_result(item, rep, order=item._exec_index, test_dirname=test_dirname)

        dur = getattr(rep, "duration", None)
        dur_s = f"{dur:.2f}s" if dur is not None else "n/a"
        LOG.info(
            f"=== END test {item._exec_index:03d}: {item.nodeid} | "
            f"outcome={rep.outcome} | duration={dur_s} | dir={test_dirname} ==="
        )
        _write_test_log_line(test_dir, f"START {item.nodeid}")
        _write_test_log_line(
            test_dir, f"END   {item.nodeid} | outcome={rep.outcome} | duration={dur_s}"
        )

    # Screenshot automático em falha (APPIUM) — respeita SAVE_ARTIFACTS
    if (
        rep.failed
        and "driver" in item.fixturenames
        and rep.when in ("call", "setup")
        and SAVE_ARTIFACTS
    ):
        test_dir = NODEID_TO_TESTDIR.get(item.nodeid)
        if test_dir:
            driver = item.funcargs.get("driver")
            if driver:
                shot_name = f"screenshot_{_sanitize(item.name)}.png"
                shot_path = test_dir / shot_name
                driver.get_screenshot_as_file(str(shot_path))
                LOG.info(f"[ARTIFACT] screenshot -> {shot_path}")
                R.add_screenshot(item, _rel_to_session(shot_path))
                _write_test_log_line(test_dir, f"ARTIFACT screenshot: {shot_name}")


# ==========================================================
# FIXTURE PARA TESTES MOBILE (APPIUM)
# ==========================================================
@pytest.fixture(scope="function")
def driver(request):
    options = AppiumOptions()
    options.load_capabilities(
        {
            "platformName": "Android",
            "deviceName": "emulator-5554",
            "automationName": "UiAutomator2",
            "appPackage": "com.b2w.americanas",
            "noReset": False,
            "fullReset": False,
            "appWaitActivity": "com.b2w.americanas.MainActivity",
            "appWaitDuration": 30000,
            "unicodeKeyboard": True,
            "resetKeyboard": True,
            "autoGrantPermissions": True,
        }
    )
    try:
        _driver = appwd.Remote("http://127.0.0.1:4723", options=options)
        if SAVE_ARTIFACTS:
            _driver.start_recording_screen()

        meta = {
            "session_id": getattr(_driver, "session_id", ""),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "capabilities": getattr(_driver, "capabilities", {}) or {},
        }
        (SESSION_DIR / "session_meta.json").write_text(
            json.dumps(meta, indent=2), encoding="utf-8"
        )

        LOG.info(f"[DRIVER] session started: {getattr(_driver, 'session_id', 'n/a')}")
    except Exception as e:
        LOG.error(f"[DRIVER] failed to create Appium driver: {type(e).__name__}: {e}")
        LOG.error(
            "Dica: verifique se o Appium Server está on em http://127.0.0.1:4723 e se o emulator-5554 está rodando (adb devices)."
        )
        pytest.skip(f"Failed to create Appium driver: {e}")

    yield _driver

    try:
        rep_call = getattr(request.node, "rep_call", None)
        rep_setup = getattr(request.node, "rep_setup", None)
        failed = (rep_call and rep_call.failed) or (rep_setup and rep_setup.failed)
        test_dir = NODEID_TO_TESTDIR.get(request.node.nodeid)

        if failed and test_dir and SAVE_ARTIFACTS:
            vid_name = f"video_{_sanitize(request.node.name)}.mp4"
            video_path = test_dir / vid_name
            data = None
            try:
                data = _driver.stop_recording_screen()
            except Exception:
                data = None
            if data:
                video_path.write_bytes(base64.b64decode(data))
                LOG.info(f"[ARTIFACT] video -> {video_path}")
                R.add_video(request.node, _rel_to_session(video_path))
                _write_test_log_line(test_dir, f"ARTIFACT video: {vid_name}")
        else:
            try:
                _ = _driver.stop_recording_screen()
            except Exception:
                pass
    finally:
        LOG.info("[DRIVER] quitting session")
        _driver.quit()


# ==========================================================
# FIXTURE PARA TESTES WEB (SELENIUM) — Chrome / Firefox
# ==========================================================
@pytest.fixture(scope="function")
def browser(request):
    """Inicializa Chrome ou Firefox para testes WEB e integra ao dashboard."""
    # prioridade: param indireto > --browser > env BROWSER > 'chrome'
    browser_name = getattr(request, "param", None)
    if not browser_name:
        browser_name = (
            request.config.getoption("--browser") or os.getenv("BROWSER", "chrome")
        ).lower()
    else:
        browser_name = str(browser_name).lower()

    notif_mode = (request.config.getoption("--notif") or "allow").lower()
    notif_map = {"allow": 1, "block": 2, "ask": 0}
    notif_value = notif_map.get(notif_mode, 1)

    if browser_name == "firefox":
        opts = FFOptions()
        opts.set_preference("permissions.default.desktop-notification", notif_value)
        opts.set_preference("permissions.default.geo", notif_value)
        opts.set_preference("dom.webnotifications.enabled", True)
        opts.set_preference("dom.push.enabled", True)

        service = FirefoxService(GeckoDriverManager().install())
        drv = swd.Firefox(service=service, options=opts)
        drv.set_window_size(1920, 1080)
    else:
        # default: chrome
        opts = ChromeOptions()
        opts.add_argument("--window-size=1920,1080")
        opts.add_experimental_option(
            "prefs",
            {"profile.default_content_setting_values.notifications": notif_value},
        )

        # 👉 usando ChromeDriverManager (funciona no Mac e no Jenkins)
        service = ChromeService(ChromeDriverManager().install())
        drv = swd.Chrome(service=service, options=opts)

    LOG.info(
        f"[WEB] Browser session started ({browser_name}). notifications={notif_mode}"
    )

    yield drv

    try:
        rep_call = getattr(request.node, "rep_call", None)
        rep_setup = getattr(request.node, "rep_setup", None)
        failed = (rep_call and rep_call.failed) or (rep_setup and rep_setup.failed)
        test_dir = NODEID_TO_TESTDIR.get(request.node.nodeid)

        if failed and test_dir and SAVE_ARTIFACTS:
            shot_name = f"screenshot_{_sanitize(request.node.name)}.png"
            shot_path = test_dir / shot_name
            drv.save_screenshot(str(shot_path))
            LOG.info(f"[WEB ARTIFACT] screenshot -> {shot_path}")
            R.add_screenshot(request.node, _rel_to_session(shot_path))
            _write_test_log_line(test_dir, f"ARTIFACT screenshot: {shot_name}")
    finally:
        LOG.info("[WEB] Quitting browser.")
        drv.quit()

# ==========================================================
# Fixtures auxiliares para APIs
# ==========================================================
@pytest.fixture(scope="session")
def base_api_url():
    """Base URL da sua API local."""
    return "http://127.0.0.1:8000"


@pytest.fixture(scope="function")
def api_client():
    """Cliente HTTP para testes de API (requests)."""
    return requests


@pytest.fixture(scope="session")
def json_data(pytestconfig):
    """Carrega o JSON de dados para os testes, a partir da raiz do projeto."""
    root_dir = Path(pytestconfig.rootpath)  # ex.: /Users/moa/cesar-automation-project
    json_path = root_dir / "data" / "testing.json"

    if not json_path.exists():
        raise FileNotFoundError(f"Arquivo JSON de testes não encontrado: {json_path}")

    with json_path.open(encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def cleanup_wishlists(api_client, base_api_url):
    """
    Limpa todas as wishlists do usuário autenticado após o teste.
    """
    yield
    url = f"{base_api_url}/wishlists"
    token = getattr(api_client, "last_token", None)
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        resp = api_client.get(url, headers=headers)
        if resp.status_code == 200:
            for w in resp.json():
                wid = w.get("id")
                if wid:
                    api_client.delete(f"{url}/{wid}", headers=headers)


@pytest.fixture
def cleanup_products(api_client, base_api_url):
    """
    Limpa todos os produtos de todas as wishlists do usuário autenticado após o teste.
    """
    yield
    base_wishlist_url = f"{base_api_url}/wishlists"
    token = getattr(api_client, "last_token", None)
    if not token:
        return
    headers = {"Authorization": f"Bearer {token}"}

    w_resp = api_client.get(base_wishlist_url, headers=headers)
    if w_resp.status_code != 200:
        return

    for wishlist in w_resp.json():
        wid = wishlist.get("id")
        if not wid:
            continue
        p_resp = api_client.get(f"{base_wishlist_url}/{wid}/products", headers=headers)
        if p_resp.status_code == 200:
            for product in p_resp.json():
                pid = product.get("id")
                if pid:
                    api_client.delete(f"{base_api_url}/products/{pid}", headers=headers)


@pytest.fixture
def cleanup_users(api_client, base_api_url):
    """
    Limpa todos os dados associados ao usuário autenticado:
    - produtos
    - wishlists
    - o próprio usuário (opcional)
    """
    yield
    token = getattr(api_client, "last_token", None)
    if not token:
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 1. Apagar produtos dentro de cada wishlist
    wl_resp = api_client.get(f"{base_api_url}/wishlists", headers=headers)
    if wl_resp.status_code == 200:
        for w in wl_resp.json() or []:
            wid = w.get("id")
            if not wid:
                continue
            prod_resp = api_client.get(
                f"{base_api_url}/wishlists/{wid}/products", headers=headers
            )
            if prod_resp.status_code == 200:
                for p in prod_resp.json() or []:
                    pid = p.get("id")
                    if pid:
                        api_client.delete(
                            f"{base_api_url}/products/{pid}", headers=headers
                        )

            api_client.delete(f"{base_api_url}/wishlists/{wid}", headers=headers)

    # 2. Apagar o próprio usuário (se a API tiver esse endpoint)
    try:
        api_client.delete(f"{base_api_url}/users/me", headers=headers)
    except Exception:
        pass
