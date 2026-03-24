from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "reports" / "daily"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def archive_daily_report(result: dict[str, Any]) -> dict[str, str]:
    trade_date = result["trade_date"]
    json_path = REPORT_DIR / f"{trade_date}.json"
    md_path = REPORT_DIR / f"{trade_date}.md"

    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(_to_markdown(result), encoding="utf-8")

    return {
        "json_path": str(json_path),
        "md_path": str(md_path),
    }


def list_archived_reports(limit: int = 30) -> list[dict[str, str]]:
    items = []
    for md_file in sorted(REPORT_DIR.glob("*.md"), reverse=True)[:limit]:
        trade_date = md_file.stem
        json_file = REPORT_DIR / f"{trade_date}.json"
        items.append(
            {
                "trade_date": trade_date,
                "md_path": str(md_file),
                "json_path": str(json_file),
            }
        )
    return items


def read_archived_report(trade_date: str) -> dict[str, str]:
    md_path = REPORT_DIR / f"{trade_date}.md"
    json_path = REPORT_DIR / f"{trade_date}.json"
    return {
        "trade_date": trade_date,
        "md": md_path.read_text(encoding="utf-8") if md_path.exists() else "",
        "json": json_path.read_text(encoding="utf-8") if json_path.exists() else "",
    }


def _to_markdown(result: dict[str, Any]) -> str:
    report = result["report"]
    lines = [
        f"# Quant Harness Daily Report - {result['trade_date']}",
        "",
        f"- Source: {result['source']}",
        f"- Run ID: {result['run_id']}",
        f"- Signal Count: {result['signal_count']}",
        f"- Validation Count: {result['validation_count']}",
        "",
        "## 中文摘要",
        report["summary_cn"],
        "",
        "## English Summary",
        report["summary_en"],
        "",
        "## 结构化日报",
        f"- 主线题材: {'、'.join(report.get('mainline_themes', [])) or '暂无'}",
        f"- 强共振候选: {'、'.join(report.get('focus_candidates', [])) or '暂无'}",
        f"- 观察名单: {'、'.join(report.get('observe_candidates', [])) or '暂无'}",
        f"- 回避名单: {'、'.join(report.get('avoid_candidates', [])) or '暂无'}",
        "",
        "### 明日计划",
    ]

    for item in report.get('tomorrow_plan', []):
        lines.append(f"- {item}")

    lines.extend([
        "",
        "## Top Signals",
    ])

    for signal in report.get("top_signals", []):
        lines.extend(
            [
                f"### {signal['name']} ({signal['symbol']})",
                f"- Strategy: {signal['strategy']}",
                f"- Score: {signal['score']}",
                f"- Risk: {signal['risk_level']}",
                f"- Theme: {signal['theme']}",
                f"- Reasons: {'; '.join(signal['reasons'])}",
                f"- Entry: {signal['entry_note']}",
                f"- Exit: {signal['exit_note']}",
                f"- Invalidation: {signal['invalidation_note']}",
                "",
            ]
        )

    return "\n".join(lines)
