"""
domain/rebecca.py - Rebecca's personality layer (Phase 2 stub).

In Phase 2 (Nurture System), this module will compose health and presence
results through Rebecca's personality, mood, and relationship state.
For now, it's a pass-through.
"""


def compose(health_result, presence_result):
    """
    Compose health and presence into Rebecca's response.

    Phase 1.5: pass-through (returns inputs unchanged).
    Phase 2: will apply mood, energy, trust modifiers.
    """
    return {
        "health": health_result,
        "presence": presence_result,
    }
