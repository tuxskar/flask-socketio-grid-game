from flask_assets import ManageAssets
from flask_script import Manager

from flask_socketio_grid_game import app

manager = Manager(app)
app.jinja_env.assets_environment.environment = app.jinja_env.assets_environment
manager.add_command("assets", ManageAssets(app.jinja_env.assets_environment))

if __name__ == "__main__":
    manager.run()
