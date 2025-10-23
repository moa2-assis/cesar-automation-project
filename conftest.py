import base64
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

import pytest
from appium import webdriver
from appium.options.common.base import AppiumOptions

from utils import reporting as R
from utils.logger import setup_logger

import csv
import requests

# ==========================================================
# CONFIGURAÇÃO RÁPIDA
# ==========================================================
# Define se o dashboard HTML será aberto automaticamente ao fim da execução
OPEN_DASHBOARD = False  # ⬅️ mude para True se quiser abrir automaticamente
# ==========================================================

# ===== estado da sessão =====
LOG = None
SESSION_DIR: Optional[Path] = None
TEST_COUNTER = 0
NODEID_TO_TESTDIR = {}


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
    (test_dir / "test_log.txt").open("a", encoding="utf-8").write(
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n"
    )


# ===== pytest lifecycle =====
@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    """Cria o 'paizinho' da sessão e inicializa o logger de sessão dentro dele."""
    global LOG, SESSION_DIR
    SESSION_DIR = Path("tests_compiled_info") / _timestamp()
    _ensure_dir(SESSION_DIR)
    LOG = setup_logger(SESSION_DIR / "session_log.txt")
    LOG.info(f"=== Pytest session STARTED ===")
    LOG.info(f"Output dir: {SESSION_DIR}")


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Gera dashboard e session_summary.json dentro do paizinho."""
    R.write_session_summary(SESSION_DIR, exitstatus)

    if OPEN_DASHBOARD:
        R.write_and_open_dashboard(SESSION_DIR)   # abre
        if LOG:
            LOG.info("[DASHBOARD] auto-open enabled → abrindo no navegador...")
    else:
        R.write_dashboard(SESSION_DIR)            # não abre
        if LOG:
            LOG.info("[DASHBOARD] auto-open desativado → apenas gerado no diretório")

    if LOG:
        LOG.info(f"=== Pytest session FINISHED (exitstatus={exitstatus}) ===")
        LOG.info(f"Dashboard: {SESSION_DIR / 'dashboard.html'}")
        LOG.info(f"Session log: {SESSION_DIR / 'session_log.txt'}")


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """Numera os testes pela ordem REAL de execução."""
    global TEST_COUNTER
    TEST_COUNTER += 1
    item._exec_index = TEST_COUNTER
    if LOG:
        LOG.info(f"=== START test {item._exec_index:03d}: {item.nodeid} ===")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Recebe o resultado por fase (setup/call/teardown), cria pasta do teste
    quando já há outcome final, salva screenshot em falha e alimenta o dashboard."""
    outcome = yield
    rep = outcome.get_result()

    setattr(item, f"rep_{rep.when}", rep)

    should_create_dir = (
        (rep.when == "call") or
        (rep.when == "setup" and rep.failed)
    )
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
        if LOG:
            LOG.info(
                f"=== END test {item._exec_index:03d}: {item.nodeid} | "
                f"outcome={rep.outcome} | duration={dur_s} | dir={test_dirname} ==="
            )
        _write_test_log_line(test_dir, f"START {item.nodeid}")
        _write_test_log_line(test_dir, f"END   {item.nodeid} | outcome={rep.outcome} | duration={dur_s}")

    if rep.failed and "driver" in item.fixturenames and rep.when in ("call", "setup"):
        test_dir = NODEID_TO_TESTDIR.get(item.nodeid)
        if test_dir:
            driver = item.funcargs.get("driver")
            if driver:
                shot_name = f"screenshot_{_sanitize(item.name)}.png"
                shot_path = test_dir / shot_name
                driver.get_screenshot_as_file(str(shot_path))
                if LOG:
                    LOG.info(f"[ARTIFACT] screenshot -> {shot_path}")
                R.add_screenshot(item, _rel_to_session(shot_path))
                _write_test_log_line(test_dir, f"ARTIFACT screenshot: {shot_name}")


@pytest.fixture(scope="function")
def driver(request):
    options = AppiumOptions()
    options.load_capabilities({
        "platformName": "Android",
        "appium:deviceName": "emulator-5554",
        "appium:automationName": "UiAutomator2",
        "appium:appPackage": "com.automationmodule",
        "appium:ensureWebviewsHavePages": True,
        "appium:nativeWebScreenshot": True,
        "appium:newCommandTimeout": 3600,
        "appium:connectHardwareKeyboard": True,
    })
    try:
        _driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
        _driver.start_recording_screen()

        meta = {
            "session_id": getattr(_driver, "session_id", ""),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "capabilities": getattr(_driver, "capabilities", {}) or {},
        }
        (SESSION_DIR / "session_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

        if LOG:
            LOG.info(f"[DRIVER] session started: {getattr(_driver, 'session_id', 'n/a')}")
    except Exception as e:
        if LOG:
            LOG.error(f"[DRIVER] failed to create Appium driver: {type(e).__name__}: {e}")
            LOG.error("Dica: verifique se o Appium Server está on em http://127.0.0.1:4723 e se o emulator-5554 está rodando (adb devices).")
        pytest.skip(f"Failed to create Appium driver: {e}")

    yield _driver

    try:
        rep_call = getattr(request.node, "rep_call", None)
        rep_setup = getattr(request.node, "rep_setup", None)
        failed = (
            (rep_call and rep_call.failed) or
            (rep_setup and rep_setup.failed)
        )
        test_dir = NODEID_TO_TESTDIR.get(request.node.nodeid)

        if failed and test_dir:
            vid_name = f"video_{_sanitize(request.node.name)}.mp4"
            video_path = test_dir / vid_name
            data = _driver.stop_recording_screen()
            if data:
                video_path.write_bytes(base64.b64decode(data))
                if LOG:
                    LOG.info(f"[ARTIFACT] video -> {video_path}")
                R.add_video(request.node, _rel_to_session(video_path))
                _write_test_log_line(test_dir, f"ARTIFACT video: {vid_name}")
        else:
            _ = _driver.stop_recording_screen()
    finally:
        if LOG:
            LOG.info("[DRIVER] quitting session")
        _driver.quit()

@pytest.fixture(scope="session")
def base_json_url():
    """Returns the base URL for the JSONPlaceholder API."""
    return "https://jsonplaceholder.typicode.com"

@pytest.fixture(scope="session")
def base_httpbin_url():
    """Returns the base URL for the httpbin API."""
    return "https://httpbin.org"

@pytest.fixture(scope="function")
def api_client():
    """Returns an API client (requests module)."""
    return requests


# ===== loader simples para CSV =====
def load_csv_test_cases(path: str):
    """Lê CSV e retorna lista de dicts (strings ‘cruas’, conversão no teste)."""
    p = Path(path)
    cases = []
    with p.open(mode="r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cases.append(row)
    return cases
