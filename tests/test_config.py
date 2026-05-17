# -*- coding: utf-8 -*-

import importlib
import os
import unittest
from unittest import mock

import app.config as config_module


class ConfigTestCase(unittest.TestCase):
    def tearDown(self):
        importlib.reload(config_module)

    def test_normalize_database_url_uses_psycopg_and_removes_channel_binding(self):
        url = "postgresql://user:pass@example.neon.tech/twelvewin?sslmode=require&channel_binding=require"

        normalized = config_module._normalize_database_url(url)

        self.assertEqual(
            "postgresql+psycopg://user:pass@example.neon.tech/twelvewin?sslmode=require",
            normalized,
        )

    def test_production_config_prefers_environment_variables(self):
        env = {
            "DATABASE_URL": "postgresql://user:pass@example.neon.tech/twelvewin?sslmode=require&channel_binding=require",
            "SECRET_KEY": "env-secret",
            "SECURITY_PASSWORD_SALT": "env-salt",
            "APP_MAIL_SERVER": "smtp.env.example",
            "APP_MAIL_PORT": "2525",
            "APP_MAIL_USE_TLS": "true",
            "APP_MAIL_USE_SSL": "false",
            "APP_MAIL_USERNAME": "env-user",
            "APP_MAIL_PASSWORD": "env-pass",
            "APP_MAIL_DEFAULT_SENDER": "env@example.com",
        }

        with mock.patch.dict(os.environ, env, clear=False):
            reloaded = importlib.reload(config_module)

        self.assertEqual("env-secret", reloaded.ProductionConfig.SECRET_KEY)
        self.assertEqual("env-salt", reloaded.ProductionConfig.SECURITY_PASSWORD_SALT)
        self.assertEqual("smtp.env.example", reloaded.ProductionConfig.MAIL_SERVER)
        self.assertEqual(2525, reloaded.ProductionConfig.MAIL_PORT)
        self.assertTrue(reloaded.ProductionConfig.MAIL_USE_TLS)
        self.assertFalse(reloaded.ProductionConfig.MAIL_USE_SSL)
        self.assertEqual("env-user", reloaded.ProductionConfig.MAIL_USERNAME)
        self.assertEqual("env-pass", reloaded.ProductionConfig.MAIL_PASSWORD)
        self.assertEqual("env@example.com", reloaded.ProductionConfig.MAIL_DEFAULT_SENDER)
        self.assertEqual(
            "postgresql+psycopg://user:pass@example.neon.tech/twelvewin?sslmode=require",
            reloaded.ProductionConfig.SQLALCHEMY_DATABASE_URI,
        )


if __name__ == "__main__":
    unittest.main()
