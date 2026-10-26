from app.routers.redirect import parse_user_agent_py

def test_parse_user_agent_desktop_chrome():
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    result = parse_user_agent_py(ua)
    assert result['device'] == 'desktop'
    assert result['os'] == 'Windows'
    assert result['browser'] == 'Chrome'

def test_parse_user_agent_mobile_android():
    ua = "Mozilla/5.0 (Linux; Android 12; SM-G998B) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36"
    result = parse_user_agent_py(ua)
    assert result['device'] == 'mobile'
    assert result['os'] == 'Android'
    assert result['browser'] == 'Chrome'

def test_parse_user_agent_edge():
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Edg/120.0.0.0"
    result = parse_user_agent_py(ua)
    assert result['browser'] == 'Edge'