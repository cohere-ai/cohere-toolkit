
import pytest

from backend.schemas.chat import EventState
from backend.schemas.context import Context
from backend.services.chat import (
    DEATHLOOP_SIMILARITY_THRESHOLDS,
    are_previous_actions_similar,
    check_death_loop,
    check_similarity,
)


def test_are_previous_actions_similar():
    distances = [
        0.5,
        0.6,
        0.8,
        0.9,
        1.0,
    ]

    assert are_previous_actions_similar(distances, 0.7, 3)


def test_are_previous_actions_not_similar():
    distances = [
        0.1,
        0.1,
        0.1,
        0.1,
    ]
    assert not are_previous_actions_similar(distances, 0.7, 3)


def test_check_similarity():
    ctx = Context()
    distances = [
        0.5,
        0.6,
        0.8,
        0.9,
        1.0,
    ]

    response = check_similarity(distances, ctx)
    assert response


def test_check_similarity_no_death_loop():
    ctx = Context()
    distances = [
        0.1,
        0.1,
        0.1,
        0.1,
    ]

    response = check_similarity(distances, ctx)
    assert not response


def test_check_similarity_not_enough_data():
    ctx = Context()
    distances = [
        0.1,
        0.1,
    ]

    response = check_similarity(distances, ctx)
    assert not response


@pytest.mark.skip(reason="We are supressing the exception while experimenting")
def test_check_death_loop_raises_on_plan():
    ctx = Context()
    event = {
        "text": "This is also a plan",
        "tool_calls": [],
    }

    event_state = EventState(
        distances_plans=[
            0.1,
            0.8,
            0.9,
        ],
        distances_actions=[
            0.1,
            0.1,
            0.1,
        ],
        previous_plan="This is a plan",
        previous_action="[]",
    )

    with pytest.raises(Exception):
        check_death_loop(event, event_state, ctx)


@pytest.mark.skip(reason="We are supressing the exception while experimenting")
def test_check_death_loop_raises_on_action():
    ctx = Context()
    event = {
        "text": "This is a plan",
        "tool_calls": [{"tool": "tool1", "args": ["This is an argument"]}],
    }

    event_state = EventState(
        distances_plans=[
            0.1,
            0.1,
            0.1,
        ],
        distances_actions=[
            0.1,
            0.8,
            0.9,
        ],
        previous_plan="Nothing like the previous plan",
        previous_action="[{'tool': 'tool1', 'args': ['This is an argument']}]",
    )

    with pytest.raises(Exception):
        check_death_loop(event, event_state, ctx)


def test_check_no_death_loop():
    ctx = Context()
    event = {
        "text": "Nothing like the previous plan",
        "tool_calls": [
            {"tool": "different_tool", "args": ["Nothing like the previous action"]}
        ],
    }

    event_state = EventState(
        distances_plans=[
            0.1,
            0.1,
            0.1,
        ],
        distances_actions=[
            0.1,
            0.1,
            0.1,
        ],
        previous_plan="This is a plan",
        previous_action='[{"tool": "tool1", "args": ["This is an argument"]}]',
    )

    new_event_state = check_death_loop(event, event_state, ctx)
    assert new_event_state.previous_plan == "Nothing like the previous plan"
    assert (
        new_event_state.previous_action
        == '[{"tool": "different_tool", "args": ["Nothing like the previous action"]}]'
    )

    assert len(new_event_state.distances_plans) == 4
    assert len(new_event_state.distances_actions) == 4

    assert new_event_state.distances_plans[-1] < max(DEATHLOOP_SIMILARITY_THRESHOLDS)
    assert new_event_state.distances_actions[-1] < max(DEATHLOOP_SIMILARITY_THRESHOLDS)
