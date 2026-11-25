-- Dynamic Dashboard: the read-only database login of the SQL datasets. Run ONCE, as a PostgreSQL superuser, on the Odoo database:
--     psql -d <odoo database> -v password="'a long random password'" -f sql_role_setup.sql
-- then give Odoo the login (never in the database): DWO_SQL_USER=dwo_sql_reader and DWO_SQL_PASSWORD=<the password> in its environment
-- (systemd: Environment=, docker: -e), and restart it. Without them a SQL dataset says "not set up" and nothing runs.
--
-- What it gives: SELECT on the columns of the public schema that do not look like credentials, nothing else, read-only transactions, a timeout, no way to create
-- anything. Odoo refuses to use a login that is a superuser or can create roles or databases. The module also refuses, whatever
-- this role can read, the tables that hold secrets (users, API keys, configuration parameters, mail and payment credentials...).
-- Re-run it after installing modules (new tables) to give the role the new ones.
\set ON_ERROR_STOP on

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'dwo_sql_reader') THEN
        CREATE ROLE dwo_sql_reader LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS CONNECTION LIMIT 40;
    END IF;
END $$;

ALTER ROLE dwo_sql_reader WITH PASSWORD :password;
ALTER ROLE dwo_sql_reader SET default_transaction_read_only = on;
ALTER ROLE dwo_sql_reader SET statement_timeout = '60s';
ALTER ROLE dwo_sql_reader SET idle_in_transaction_session_timeout = '30s';

DO $$
BEGIN
    EXECUTE format('GRANT CONNECT ON DATABASE %I TO dwo_sql_reader', current_database());
END $$;
REVOKE CREATE ON SCHEMA public FROM dwo_sql_reader;
GRANT USAGE ON SCHEMA public TO dwo_sql_reader;

-- Start from nothing, then give SELECT on every column EXCEPT the ones that look like credentials (password, secret, token, api key,
-- private key, otp...), wherever they are. This is what keeps secrets out of a query: Odoo refuses a login that can read such a column.
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM dwo_sql_reader;
DO $$
DECLARE r record;
BEGIN
    FOR r IN
        SELECT c.relname AS tbl, array_agg(quote_ident(a.attname) ORDER BY a.attnum) AS cols
          FROM pg_class c
          JOIN pg_namespace n ON n.oid = c.relnamespace
          JOIN pg_attribute a ON a.attrelid = c.oid AND a.attnum > 0 AND NOT a.attisdropped
         WHERE n.nspname = 'public' AND c.relkind IN ('r', 'v', 'm', 'p')
           AND a.attname !~* '(password|passwd|secret|token|api_?key|private|pkcs|credential|signing_key|totp|otp_|backup_code|webhook|salt$|_hash$|^hash$)'
         GROUP BY c.relname
    LOOP
        EXECUTE format('GRANT SELECT (%s) ON public.%I TO dwo_sql_reader', array_to_string(r.cols, ', '), r.tbl);
    END LOOP;
END $$;

-- and the tables that hold secrets as a whole: not readable at all (the module refuses them too)
DO $$
DECLARE t text;
BEGIN
    FOREACH t IN ARRAY ARRAY['res_users', 'res_users_apikeys', 'res_users_apikeys_description', 'res_users_identitycheck',
                             'res_users_settings', 'res_users_log', 'auth_totp_device', 'auth_passkey_key', 'ir_config_parameter',
                             'ir_mail_server', 'fetchmail_server', 'iap_account', 'payment_provider', 'payment_token',
                             'auth_oauth_provider', 'ir_cron', 'ir_actions_server', 'ir_module_module', 'ir_model_data',
                             'certificate_certificate', 'mail_mail']
    LOOP
        IF to_regclass('public.' || t) IS NOT NULL THEN
            EXECUTE format('REVOKE ALL ON public.%I FROM dwo_sql_reader', t);
        END IF;
    END LOOP;
END $$;
