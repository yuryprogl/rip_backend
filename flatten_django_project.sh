#!/bin/bash
# Собирает ключевые файлы Django-проекта в единый текстовый файл с путями.

ROOT_DIR="${1:-.}"                                # Корень проекта
OUTPUT_FILE="${2:-django_project_flattened.txt}"   # Имя итогового файла

# Включаем только важные типы файлов (исходники, шаблоны, конфиги)
INCLUDE_EXTENSIONS=("py" "html" "htm" "css" "js" "json" "yaml" "yml" "ini" "cfg" "toml" "md")

# Исключаем неключевые директории
EXCLUDE_DIRS=(.git .idea .vscode venv env .env __pycache__ static media migrations node_modules .cache build dist)

# Очистим старый файл
> "$OUTPUT_FILE"

# Проверка: нужно ли исключить путь
should_exclude() {
  local path="$1"
  for dir in "${EXCLUDE_DIRS[@]}"; do
    if [[ "$path" == *"/$dir"* ]]; then
      return 0
    fi
  done
  return 1
}

echo "📦 Собираем ключевые файлы Django-проекта из $ROOT_DIR ..."

# Основной цикл по всем файлам
while IFS= read -r -d '' file; do
  should_exclude "$file" && continue

  # Проверяем по расширению
  match=false
  for ext in "${INCLUDE_EXTENSIONS[@]}"; do
    if [[ "$file" == *.$ext ]]; then
      match=true
      break
    fi
  done
  $match || continue

  # Добавляем заголовок файла
  echo -e "\n\n### FILE: ${file#$ROOT_DIR/}" >> "$OUTPUT_FILE"
  echo "================================================================================" >> "$OUTPUT_FILE"
  
  # Пишем содержимое (если возможно прочитать)
  cat "$file" >> "$OUTPUT_FILE" 2>/dev/null || echo "⚠️ [Ошибка чтения]" >> "$OUTPUT_FILE"

  echo -e "\n================================================================================" >> "$OUTPUT_FILE"

done < <(find "$ROOT_DIR" -type f -print0)

# Итоговая статистика
FILES_COUNT=$(grep -c "^### FILE:" "$OUTPUT_FILE" || echo 0)
echo -e "\n\n📊 ИТОГО: $FILES_COUNT файлов собрано в $OUTPUT_FILE"
echo "✅ Готово."
