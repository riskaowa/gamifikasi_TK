from app import create_app
from datetime import datetime

app = create_app()
with app.app_context():
    client = app.test_client()
    resp = client.post('/login', data={'username': 'murid1', 'password': 'murid123', 'role': 'murid'}, follow_redirects=True)
    print('Login', resp.status_code)
    resp = client.get('/misi-harian')
    print('Misi', resp.status_code)
    txt = resp.get_data(as_text=True)
    print('Has question block:', 'Soal <span id="current-number">1</span> dari 2' in txt)
    print('Has img:', '<img' in txt)
    print('Now', datetime.now())
