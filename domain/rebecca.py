"""
domain/rebecca.py - Rebecca's personality layer.

Composes health, presence, and nurture results with personality modulation.
Mood-based voice line selection from constants.REBECCA_VOICE_MESSAGES.
"""

import random

from domain.constants import REBECCA_VOICE_MESSAGES


def compose(health_result, presence_result, nurture_result=None):
    """
    Compose health, presence, and nurture into Rebecca's response.

    Args:
        health_result: dict - health evaluation result
        presence_result: dict - presence evaluation result
        nurture_result: dict or None - nurture evaluation result

    Returns:
        dict - composed result with optional voice
    """
    result = {
        "health": health_result,
        "presence": presence_result,
    }
    if nurture_result:
        result["nurture"] = nurture_result
        result["voice"] = select_voice(nurture_result.get("mood", {}))
    return result


def select_voice(mood_data):
    """
    Select Rebecca's voice line based on current mood state.

    Args:
        mood_data: dict - mood data with "state" key

    Returns:
        dict - {state, message} where message is a randomly chosen voice line
    """
    state = mood_data.get("state", "normal") if mood_data else "normal"
    pool = REBECCA_VOICE_MESSAGES.get(state, REBECCA_VOICE_MESSAGES["normal"])
    return {
        "state": state,
        "message": random.choice(pool),
    }
