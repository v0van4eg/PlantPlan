-- SQL-скрипт для обновления существующей базы данных
-- Добавление поля archived к таблице plants для возможности архивирования растений

-- Проверяем, существует ли уже столбец archived в таблице plants
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'plants' AND column_name = 'archived') THEN
        -- Добавляем столбец archived в таблицу plants
        ALTER TABLE plants ADD COLUMN archived BOOLEAN DEFAULT FALSE;
        
        -- Обновляем существующие записи, чтобы archived был FALSE по умолчанию
        UPDATE plants SET archived = FALSE WHERE archived IS NULL;
        
        RAISE NOTICE 'Столбец archived успешно добавлен в таблицу plants';
    ELSE
        RAISE NOTICE 'Столбец archived уже существует в таблице plants';
    END IF;
END $$;

-- Проверяем структуру таблицы plants
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'plants' AND column_name = 'archived';

-- Проверяем количество архивных растений
SELECT COUNT(*) as archived_plants_count FROM plants WHERE archived = TRUE;

-- Показываем все растения с новым полем для проверки
SELECT id, name, species, archived FROM plants ORDER BY id;

-- Создаем индекс для улучшения производительности при фильтрации по архивным растениям
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE tablename = 'plants' AND indexname = 'idx_plants_archived') THEN
        CREATE INDEX idx_plants_archived ON plants (archived);
        RAISE NOTICE 'Индекс для столбца archived успешно создан';
    ELSE
        RAISE NOTICE 'Индекс для столбца archived уже существует';
    END IF;
END $$;