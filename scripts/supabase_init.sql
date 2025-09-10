-- === ENUMS ===
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'order_status') THEN
    CREATE TYPE order_status AS ENUM (
      'pending',     -- 주문 접수 (입금 확인 전)
      'accepted',    -- 관리자 승인
      'preparing',   -- 조리 중
      'ready',       -- 준비 완료
      'served',      -- 서빙 완료
      'canceled',    -- 취소됨
      'deleted'      -- 삭제됨
    );
  END IF;
END$$;

-- === TABLES ===
CREATE TABLE IF NOT EXISTS public.tables (
  id SERIAL PRIMARY KEY,
  table_no INT UNIQUE NOT NULL CHECK (table_no > 0)
);

CREATE TABLE IF NOT EXISTS public.menu_items (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  price INT NOT NULL CHECK (price >= 0),
  is_available BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS public.orders (
  id BIGSERIAL PRIMARY KEY,
  table_id INT REFERENCES public.tables(id),
  customer_name TEXT,                           -- 입금자명 / 고객명
  order_code TEXT UNIQUE NOT NULL,              -- 주문 고유 코드
  order_status order_status NOT NULL DEFAULT 'pending',
  amount_total INT NOT NULL CHECK (amount_total >= 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS public.order_items (
  id BIGSERIAL PRIMARY KEY,
  order_id BIGINT REFERENCES public.orders(id) ON DELETE CASCADE,
  menu_item_id BIGINT REFERENCES public.menu_items(id),
  qty INT NOT NULL CHECK (qty > 0),
  price_unit INT NOT NULL CHECK (price_unit >= 0),
  amount INT GENERATED ALWAYS AS (qty * price_unit) STORED
);

-- (선택) 주문 상태 이력 / 감사 로그
CREATE TABLE IF NOT EXISTS public.order_events (
  id BIGSERIAL PRIMARY KEY,
  order_id BIGINT REFERENCES public.orders(id) ON DELETE CASCADE,
  from_status order_status,
  to_status order_status NOT NULL,
  reason TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- === INDEXES (조회 최적화) ===
CREATE INDEX IF NOT EXISTS idx_orders_order_code ON public.orders(order_code);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON public.orders(created_at);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON public.order_items(order_id);

-- === REALTIME PUBLICATION (프론트 구독용) ===
ALTER PUBLICATION supabase_realtime ADD TABLE public.orders;
ALTER PUBLICATION supabase_realtime ADD TABLE public.order_items;
