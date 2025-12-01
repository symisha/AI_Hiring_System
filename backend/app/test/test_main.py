from backend.app.database.db_queries.profile_db import profile_preview_query

def test_profile_preview(user):
    result = profile_preview_query(user)
    print(result)
    assert "username" in result
    assert "industry" in result
    assert "email" in result
    #assert "location" in result