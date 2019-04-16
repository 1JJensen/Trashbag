from pathlib import Path

from rlbottraining.common_exercises.rl_custom_training_import.rl_importer import import_exercises
from rlbottraining.paths import _example_rl_custom_training_json

from rlbot.matchconfig.match_config import PlayerConfig, Team

def make_default_playlist():
    exercises = import_exercises(_example_rl_custom_training_json)
    exercises.pop(14) # 14 doesnt end properly
    exercises.pop(23) # 24 doesnt end properly
    exercises.pop(24) # 26 doesnt end properly
    for exercise in exercises:
        exercise.match_config.player_configs = [
            PlayerConfig.bot_config(
                Path(__file__).absolute().parent / 'Trashbag' / 'Trashbag.cfg',
                Team.BLUE
            )
        ]
    return exercises