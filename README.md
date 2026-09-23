Источник и контрольный срез
В качестве источника используются локальные CSV-файлы (raw_customers.csv, raw_orders.csv), имитирующие выгрузку из системы E-commerce.
Контрольный срез: 3 клиента, 4 заказа за период с 2023-10-01 по 2023-10-02. 
Требование
Построить ежедневный отчет для коммерческого директора, показывающий выручку и количество заказов в разрезе регионов клиентов. Ключевое требование: регион клиента должен фиксироваться на момент совершения покупки (историческая атрибуция).
Схема и гранулярность
Гранулярность факта: Одна строка таблицы fct_orders — это один уникальный заказ (order_id).
Схема: Звезда (Star Schema).
Факт: fct_orders (ключи: customer_sk, date_sk).
Измерения: dim_customers (SCD Type 2), dim_date.
Витрина: mart_daily_sales (агрегация по дню и региону).
Решение по истории (SCD2)
Для измерения dim_customers используется стратегия SCD Type 2 через механизм dbt snapshots.
Обоснование: Если клиент переедет из региона "North" в "South", мы не должны переписывать его прошлые заказы. SCD2 позволяет хранить интервалы времени (dbt_valid_from, dbt_valid_to), что гарантирует корректную атрибуцию исторической выручки.
Версии инструментов
OS: Ubuntu 24.04 (WSL2)
Python: 3.12
PostgreSQL: 16
Apache Airflow: 2.9.3
dbt-core: 1.12.5, dbt-postgres: 1.11.0

Команды запуска с нуля
# 1. Подготовка окружения и БД
sudo apt install postgresql python3-venv -y
sudo -u postgres psql -c "CREATE USER airflow WITH PASSWORD 'airflow';"
sudo -u postgres psql -c "CREATE DATABASE dwh OWNER airflow;"

# 2. Установка зависимостей
python3 -m venv venv && source venv/bin/activate
pip install apache-airflow==2.9.3 dbt-postgres psycopg2-binary pandas setuptools

# 3. Инициализация Airflow
export AIRFLOW_HOME=~/airflow
export AIRFLOW__CORE__LOAD_EXAMPLES=False
airflow db init && airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com

# 4. Запуск сервисов
airflow webserver --port 8080 --host 0.0.0.0
# (в другом терминале) airflow scheduler

# 5. Запуск dbt вручную (опционально)
cd dbt_project && dbt deps && dbt run --profiles-dir .
