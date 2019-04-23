from rlbottraining.common_exercises.bronze_goalie import HookShot
from pathlib import Path
from rlbot.matchconfig.match_config import PlayerConfig, Team
def make_default_playlist():
    exercises = [HookShot('Trash Training')]

    for exercise in exercises:
        exercise.match_config.player_configs = [
            PlayerConfig.bot_config(
                Path(__file__).absolute().parent.parent / 'Trashbag' / 'Trashbag.cfg', 
                Team.BLUE
            )
        ]
    return exercises