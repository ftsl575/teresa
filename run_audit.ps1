Set-Location "C:\Users\G\Desktop\teresa\spec_classifier"

# 1) Пайплайн — все 3 вендора
python main.py --batch-dir C:\Users\G\Desktop\INPUT\dell --vendor dell --output-dir C:\Users\G\Desktop\OUTPUT
python main.py --batch-dir C:\Users\G\Desktop\INPUT\hpe --vendor hpe --output-dir C:\Users\G\Desktop\OUTPUT
python main.py --batch-dir C:\Users\G\Desktop\INPUT\cisco --vendor cisco --output-dir C:\Users\G\Desktop\OUTPUT

# 2) Аудит с AI — запрос ключа перед запуском
$key = Read-Host "OpenAI API Key" -AsSecureString
$env:OPENAI_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($key)
)
python batch_audit.py --output-dir C:\Users\G\Desktop\OUTPUT --model gpt-4o-mini

# 3) Кластеризация
python cluster_audit.py --output-dir C:\Users\G\Desktop\OUTPUT
