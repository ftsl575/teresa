Set-Location "C:\Users\G\Desktop\teresa\spec_classifier"

# 1) Пайплайн — все 3 вендора
python main.py --batch-dir C:\Users\G\Desktop\INPUT\dell --vendor dell --output-dir C:\Users\G\Desktop\OUTPUT
python main.py --batch-dir C:\Users\G\Desktop\INPUT\hpe --vendor hpe --output-dir C:\Users\G\Desktop\OUTPUT
python main.py --batch-dir C:\Users\G\Desktop\INPUT\cisco --vendor cisco --output-dir C:\Users\G\Desktop\OUTPUT

# 2) Аудит с AI
$env:OPENAI_API_KEY="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"
python batch_audit.py --output-dir C:\Users\G\Desktop\OUTPUT --model gpt-4o-mini

# 3) Кластеризация
python cluster_audit.py --output-dir C:\Users\G\Desktop\OUTPUT
