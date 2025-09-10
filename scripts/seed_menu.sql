-- === 샘플 테이블 번호 ===
INSERT INTO public.tables (table_no) VALUES
  (1),
  (2),
  (3),
  (4),
  (10),
  (12)
ON CONFLICT (table_no) DO NOTHING;

-- === 메뉴 이름 유니크 제약 (최초 실행 시에만 추가) ===
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'uq_menu_name'
  ) THEN
    ALTER TABLE public.menu_items
      ADD CONSTRAINT uq_menu_name UNIQUE (name);
  END IF;
END$$;

-- === 샘플 메뉴 ===
INSERT INTO public.menu_items (name, price, is_available) VALUES
  ('TNT 김치볶음밥', 10000, TRUE),
  ('철광석 주먹밥', 3500, TRUE),
  ('케이크 감자전', 8000, TRUE),
  ('황금사과', 7000, TRUE),
  ('스티브가 잡은 물고기탕', 12000, TRUE),
  ('수상한 스튜', 9000, TRUE)
ON CONFLICT (name) DO NOTHING;
