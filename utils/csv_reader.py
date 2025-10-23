# utils/csv_reader.py
import csv
import json
from pathlib import Path

CSV_DIR = Path("csv_tests")


def _parse_json_or_none(val):
    if val is None:
        return None
    val = val.strip()
    if not val:
        return None
    try:
        return json.loads(val)
    except Exception:
        return None  # mantém “burrinho”: se não for JSON válido, ignora


def load_all_csv_cases():
    """
    Lê todos os .csv em csv_tests/ e retorna uma lista de dicts.
    Colunas suportadas (use só as que precisar):
      - name            (texto livre pro id do teste)
      - method          (GET|POST|PUT|PATCH|DELETE)
      - url             (pode ser absoluta ou caminho tipo /posts)
      - base            (opcional: json|httpbin; ajuda a montar a URL com fixtures)
      - headers         (opcional: JSON ex: {"X-Custom":"1"})
      - params          (opcional: JSON ex: {"q":"foo"})
      - json            (opcional: JSON body)
      - expect_status   (ex: 200)
      - assert_path     (opcional: caminho no JSON, ex: "0.title" ou "owner.login")
      - expect_value    (opcional: compara com o valor de assert_path)
      - contains        (opcional: substring no corpo textual)
    """
    cases = []
    if not CSV_DIR.exists():
        return cases
    for p in sorted(CSV_DIR.glob("*.csv")):
        with p.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # normalizações “burrinhas”
                row["_file"] = p.name
                row["method"] = (row.get("method") or "GET").strip().upper()
                row["url"] = (row.get("url") or "").strip()
                row["base"] = (row.get("base") or "").strip().lower()
                row["headers"] = _parse_json_or_none(row.get("headers"))
                row["params"] = _parse_json_or_none(row.get("params"))
                row["json"] = _parse_json_or_none(row.get("json"))
                try:
                    row["expect_status"] = int(row.get("expect_status") or 200)
                except ValueError:
                    row["expect_status"] = 200
                row["assert_path"] = (row.get("assert_path") or "").strip()
                row["expect_value"] = (row.get("expect_value") or "").strip()
                row["contains"] = (row.get("contains") or "").strip()
                row["name"] = (
                    row.get("name") or f"{p.stem}:{row['method']} {row['url']}"
                ).strip()
                cases.append(row)
    return cases


def dot_get(data, path):
    """
    Busca “burrinha” por caminho tipo: "0.title" ou "owner.login" ou "items.0.name"
    Suporta listas e dicts. Se não achar, retorna None.
    """
    if not path:
        return None
    cur = data
    for part in path.split("."):
        if isinstance(cur, list):
            try:
                idx = int(part)
            except ValueError:
                return None
            if 0 <= idx < len(cur):
                cur = cur[idx]
            else:
                return None
        elif isinstance(cur, dict):
            if part in cur:
                cur = cur[part]
            else:
                return None
        else:
            return None
    return cur