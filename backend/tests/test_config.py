from app.config.config import settings

def test_project_name():
    """Verify that settings can load from the environment configurations."""
    assert settings.PROJECT_NAME == "AI Augmented Pitch Analyser"
    assert settings.API_V1_STR == "/api"
