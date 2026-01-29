import json
import os
import re
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from google.cloud import bigquery
import google.generativeai as genai
from dotenv import load_dotenv


APP_NAME = "text-to-sql-api"
DEFAULT_LIMIT = 100
PROHIBITED_TOKENS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "MERGE",
    "CREATE",
    "ALTER",
    "DROP",
    "TRUNCATE",
    "CALL",
    "EXECUTE",
    "GRANT",
    "REVOKE",
]


def load_schema_text(schema_path: str) -> str:
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def strip_code_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n", "", text)
        text = text.replace("```", "").strip()
    return text


def ensure_single_statement(sql: str) -> str:
    parts = [p.strip() for p in sql.split(";") if p.strip()]
    if len(parts) > 1:
        raise ValueError("複数のSQLステートメントは許可されていません。")
    return parts[0] if parts else ""


def ensure_select_only(sql: str) -> None:
    upper = sql.upper()
    if not upper.startswith("SELECT"):
        raise ValueError("SELECT文のみ許可されています。")
    for token in PROHIBITED_TOKENS:
        if re.search(rf"\b{token}\b", upper):
            raise ValueError("SELECT以外の操作は許可されていません。")


def ensure_limit(sql: str, limit: int) -> str:
    if re.search(r"\bLIMIT\b", sql, flags=re.IGNORECASE):
        return sql
    return f"{sql.rstrip()}\nLIMIT {limit}"


def validate_sql(sql: str) -> str:
    sql = strip_code_fence(sql)
    sql = ensure_single_statement(sql)
    ensure_select_only(sql)
    return sql


def build_prompt(text: str, dataset: str, project_id: str, schema_text: str) -> str:
    schema_block = schema_text.strip() or "（スキーマ情報なし）"
    return (
        "あなたはBigQuery向けのSQL生成アシスタントです。\n"
        "以下の条件を必ず守ってください:\n"
        "- SELECT文のみを生成する\n"
        "- DDL/DMLは使わない\n"
        "- 可能な限りSELECT *を避ける\n"
        "- テーブルは `project.dataset.table` 形式で指定する\n"
        "- BigQueryの標準SQLのみを使用し、他DBの関数は使わない\n"
        f"- projectは `{project_id}`、datasetは `{dataset}` を使う\n"
        "- SQLだけを返し、説明は不要\n\n"
        "テーブル定義:\n"
        f"{schema_block}\n\n"
        "ユーザーの要求:\n"
        f"{text}\n"
    )


class GenerateRequest(BaseModel):
    text: Optional[str] = Field(None, description="自然言語での問い合わせ")
    user_prompt: Optional[dict] = Field(None, description="ユーザープロンプト(JSON)")


class GenerateResponse(BaseModel):
    sql: str


class ExecuteRequest(BaseModel):
    sql: str
    dry_run: bool = False
    max_bytes_billed: Optional[int] = None


class ExecuteResponse(BaseModel):
    total_rows: int
    rows: list[dict]
    bytes_processed: int
    cache_hit: bool


def create_app() -> FastAPI:
    app = FastAPI(title=APP_NAME)

    load_dotenv()

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    dataset_id = os.getenv("BQ_DATASET", "ecommerce")
    location = os.getenv("BQ_LOCATION")
    max_bytes_default = int(os.getenv("BQ_MAX_BYTES_BILLED", "104857600"))  # 100MB
    schema_path = os.getenv("SCHEMA_PATH", "schema.sql")
    sql_output_path = os.getenv("SQL_OUTPUT_PATH", "generated.sql")
    schema_text = load_schema_text(schema_path)

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    if not project_id:
        raise RuntimeError("GOOGLE_CLOUD_PROJECTが未設定です。")
    if not gemini_api_key:
        raise RuntimeError("GEMINI_API_KEYが未設定です。")

    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel(gemini_model)
    bq_client = bigquery.Client(project=project_id, location=location)

    @app.post("/generate", response_model=GenerateResponse)
    def generate_sql(req: GenerateRequest) -> GenerateResponse:
        if req.user_prompt is not None:
            user_text = json.dumps(req.user_prompt, ensure_ascii=False, indent=2)
        elif req.text:
            user_text = req.text
        else:
            raise HTTPException(status_code=400, detail="text か user_prompt のどちらかを指定してください。")

        prompt = build_prompt(user_text, dataset_id, project_id, schema_text)
        response = model.generate_content(prompt)
        sql = validate_sql(response.text or "")
        sql = ensure_limit(sql, DEFAULT_LIMIT)
        try:
            Path(sql_output_path).write_text(f"{sql}\n", encoding="utf-8")
        except OSError as exc:
            raise HTTPException(status_code=500, detail=f"SQLの保存に失敗しました: {exc}") from exc
        return GenerateResponse(sql=sql)

    @app.post("/execute", response_model=ExecuteResponse)
    def execute_sql(req: ExecuteRequest) -> ExecuteResponse:
        sql = validate_sql(req.sql)
        sql = ensure_limit(sql, DEFAULT_LIMIT)

        job_config = bigquery.QueryJobConfig(
            use_query_cache=True,
            maximum_bytes_billed=req.max_bytes_billed or max_bytes_default,
            dry_run=req.dry_run,
        )
        job = bq_client.query(sql, job_config=job_config)

        if req.dry_run:
            return ExecuteResponse(
                total_rows=0,
                rows=[],
                bytes_processed=job.total_bytes_processed or 0,
                cache_hit=False,
            )

        results = list(job.result())
        rows = [dict(row.items()) for row in results]
        return ExecuteResponse(
            total_rows=job.num_dml_affected_rows or len(rows),
            rows=rows,
            bytes_processed=job.total_bytes_processed or 0,
            cache_hit=bool(job.cache_hit),
        )

    return app


app = create_app()

