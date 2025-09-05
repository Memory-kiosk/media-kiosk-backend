# media-kiosk-backend

## Tech Stack

- **Framework**: FastAPI, Starlette
- **Server**: Uvicorn
- **DB/ORM**: PostgreSQL (Supabase) + SQLAlchemy + Alembic
- **Driver**: psycopg / psycopg-binary
- **Config**: python-dotenv
- **HTTP Client**: httpx (Toss API 연동)
- **Logging**: loguru
- **Test**: pytest, pytest-asyncio

## Initial Setup

### 1. Conda 가상환경 생성

```bash
conda create -n kiosk-backend python=3.11 -y
conda activate kiosk-backend
```

### 2. 패키치 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 (.env)

```
# FastAPI
APP_ENV=local
APP_PORT=8000

# Supabase DB
DATABASE_URL=postgresql+psycopg://postgres:<PW>@db.<PROJECT>.supabase.co:5432/postgres

# Supabase Realtime (프론트용)
SUPABASE_URL=https://<PROJECT>.supabase.co
SUPABASE_ANON_KEY=<anon_public_key>

# Toss Payments
TOSS_SECRET_KEY=sk_test_xxxxxxxxx
TOSS_WEBHOOK_BASIC=base64(username:password)  # (선택)

# Admin 인증 (API Key)
ADMIN_API_KEY=supersecret123
```

### 4. Supabase 초기 설정

1. Supabase 프로젝트 생성 → Project Settings에서 DB URL/비밀번호 확인
2. SQL Editor에서 `supabase_init.sql`  실행 (ENUM, 테이블 생성)
3. Realtime publication 확인

```sql
SELECT schemaname, tablename
FROM pg_publication_tables
WHERE pubname = 'supabase_realtime'
ORDER BY schemaname, tablename;
```

1. 만약 안된다면 Realtime publication 추가:

```sql
alter publication supabase_realtime add table public.orders;
alter publication supabase_realtime add table public.order_items;
```

1. `seed_menu.sql`로 샘플 메뉴 데이터 삽입

## 실행 방법

```bash
uvicorn app.main:app --reload --port 8000
```

Swagger UI → [http://localhost:8000/docs](http://localhost:8000/docs)

## 전체 플로우

1. 고객 → 주문 생성 (`POST /orders`) → `order_code` 발급
2. 고객 → Toss 결제 (orderId = order_code)
3. Toss → 서버 Webhook 호출 (`/payments/toss/callback`)
4. 서버 → 금액 검증 후 `payment_status=paid`, `order_status=accepted` 업데이트
5. Supabase Realtime → 관리자 페이지에 실시간 반영
6. 관리자 → 주문 상태 변경 (`PATCH /orders/{id}/status`) 또는 삭제