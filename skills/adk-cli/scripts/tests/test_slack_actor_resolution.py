from __future__ import annotations

import slack_helpers


def _client_with_members(members: list[dict]):
    client = object.__new__(slack_helpers.SlackClient)
    client._user_cache = {}

    def _call(method, params):
        assert method == "users_list"
        return {"members": members, "response_metadata": {}}

    client._call = _call
    return client


def test_resolve_human_user_name_to_user_id():
    client = _client_with_members([
        {
            "id": "U123",
            "name": "sujeet",
            "real_name": "Sujeet Jaiswal",
            "profile": {"display_name": "Sujeet Jaiswal"},
        }
    ])

    assert client.resolve_user_token_ids("@Sujeet Jaiswal") == {"U123"}
    assert client.resolve_user_token("@Sujeet Jaiswal") == "U123"


def test_resolve_bot_app_name_to_all_actor_ids():
    client = _client_with_members([
        {
            "id": "U999BOT",
            "name": "sujeets-bot",
            "real_name": "Sujeet's Bot",
            "is_bot": True,
            "profile": {
                "display_name": "Sujeet's Bot",
                "bot_id": "B999BOT",
                "api_app_id": "A999APP",
            },
        }
    ])

    assert client.resolve_user_token_ids("@Sujeet's Bot") == {
        "U999BOT",
        "B999BOT",
        "A999APP",
    }
    assert client.resolve_user_token("@Sujeet's Bot") == "U999BOT"


def test_extract_message_actor_ids_includes_user_bot_and_app_ids():
    ids = set(slack_helpers.extract_message_actor_ids({
        "user": "U123",
        "bot_id": "B999BOT",
        "app_id": "A999APP",
        "text": "cc <@U456>",
    }))

    assert ids == {"U123", "B999BOT", "A999APP", "U456"}
