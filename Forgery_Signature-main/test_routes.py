from app import app
with app.app_context():
    routes = [rule.endpoint for rule in app.url_map.iter_rules() if 'static' not in rule.endpoint]
    print("Available routes:", routes)
    if 'history' in routes:
        print("✅ history route found!")
    else:
        print("❌ history route NOT found")
    if 'delete_history' in routes:
        print("✅ delete_history route found!")
    else:
        print("❌ delete_history route NOT found")
