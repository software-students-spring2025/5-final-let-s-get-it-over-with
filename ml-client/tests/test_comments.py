"""
Some tests for the ml-client
"""

# pylint: disable=too-few-public-methods
# pylint: disable=redefined-outer-name
import random
import pytest


def generate_twitch_comment(
    session_username, expression, encoded_image, openai_client, user_pool
):
    """Generates a comment based on the logic from comments.py."""
    reaction_prompt = (
        f"Write a short, fun, Twitch-style comment reacting to a webcam stream "
        f"where the streamer looks like they're {expression}. Spam emojis and keep it casual."
    )
    video_prompt = "React to this frame from the stream"

    # 60% chance: video-based comment, 40% chance: reaction-based comment
    prompt = video_prompt if random.random() < 0.6 else reaction_prompt

    # Call OpenAI to generate the comment
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    f'You are one of thousands of viewers of live streamer "{session_username}" '
                    "and love to participate in the chat. "
                    "You are funny, type fast, use twitch lingo like pog, lmao, kek, "
                    "and also ask occasional questions. "
                    "Keep your responses short, less than 5 words."
                    "Respond in either all lowercase or all caps."
                ),
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url", 
                        "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"},
                    },
                ],
            },
        ],
        temperature=0.8,
        presence_penalty=0.3,
        max_tokens=20,
    )

    # Extract the comment
    message = response.choices[0].message.content

    # Pick a random username from the pool
    username = random.choice(user_pool)

    return {
        "comment": message,
        "username": username,
    }


class FakeMessage:
    """Simulates a message object with content."""

    def __init__(self, content):
        self.content = content


class FakeChoice:
    """Simulates a choice object with a message."""

    def __init__(self, content):
        self.message = FakeMessage(content)


class FakeResponse:
    """Simulates a set response object with given choices."""

    def __init__(self):
        self.choices = [FakeChoice("OMEGALUL")]


class FakeCompletions:
    """Fake completions endpoint."""

    @staticmethod
    def create(model, messages, temperature, presence_penalty, max_tokens):
        """returns given dummy reponse"""
        # pylint: disable=unused-argument
        return FakeResponse()


class FakeChat:
    """Fake chat endpoint."""

    completions = FakeCompletions()


class FakeOpenAIClient:
    """Fake OpenAI client."""

    chat = FakeChat()


class FakeErrorCompletions:
    """Fake completions that always raise an error."""

    @staticmethod
    def create(model, messages, temperature, presence_penalty, max_tokens):
        """raise runtime error regardless of choices"""
        raise RuntimeError("Simulated OpenAI failure")


class FakeErrorChat:
    """Fake chat that always fails."""

    completions = FakeErrorCompletions()


class FakeOpenAIClientError:
    """Fake OpenAI client that simulates an error."""

    chat = FakeErrorChat()


@pytest.fixture
def setup_test_data():
    """Creates dummy data for testing."""
    fake_openai_client = FakeOpenAIClient()
    user_pool = ["UserA", "UserB", "UserC"]
    session_username = "TestStreamer"
    encoded_image = "fakeimage"
    return fake_openai_client, user_pool, session_username, encoded_image


def test_comment_generation_with_reaction_prompt(setup_test_data):
    """Tests comment generation with a reaction prompt."""
    fake_openai_client, user_pool, session_username, encoded_image = setup_test_data
    random.seed(999)  # Force random.random() > 0.6
    expression = "smiling"

    result = generate_twitch_comment(
        session_username=session_username,
        expression=expression,
        encoded_image=encoded_image,
        openai_client=fake_openai_client,
        user_pool=user_pool,
    )

    assert result["comment"] == "OMEGALUL"
    assert isinstance(result["comment"], str)
    assert result["comment"].isupper() or result["comment"].islower()
    assert result["username"] in user_pool
    assert isinstance(result["username"], str)
    assert len(result["comment"]) <= 20


def test_comment_generation_with_video_prompt(setup_test_data):
    """Tests comment generation with a video prompt."""
    fake_openai_client, user_pool, session_username, encoded_image = setup_test_data
    random.seed(1)  # Force random.random() < 0.6
    expression = "neutral"

    result = generate_twitch_comment(
        session_username=session_username,
        expression=expression,
        encoded_image=encoded_image,
        openai_client=fake_openai_client,
        user_pool=user_pool,
    )

    assert result["comment"] == "OMEGALUL"
    assert isinstance(result["comment"], str)
    assert result["comment"].isupper() or result["comment"].islower()
    assert result["username"] in user_pool
    assert isinstance(result["username"], str)
    assert len(result["comment"]) <= 20


def test_comment_generation_with_empty_user_pool(setup_test_data):
    """Tests comment generation with an empty user pool."""
    fake_openai_client, _, session_username, encoded_image = setup_test_data
    empty_user_pool = []  # No users
    expression = "waving"

    with pytest.raises(IndexError):
        generate_twitch_comment(
            session_username=session_username,
            expression=expression,
            encoded_image=encoded_image,
            openai_client=fake_openai_client,
            user_pool=empty_user_pool,
        )


def test_openai_client_failure():
    """Tests behavior when OpenAI client fails."""
    fake_error_openai_client = FakeOpenAIClientError()
    user_pool = ["UserA", "UserB", "UserC"]
    session_username = "TestStreamer"
    encoded_image = "fakeimage"
    expression = "neutral"

    with pytest.raises(RuntimeError, match="Simulated OpenAI failure"):
        generate_twitch_comment(
            session_username=session_username,
            expression=expression,
            encoded_image=encoded_image,
            openai_client=fake_error_openai_client,
            user_pool=user_pool,
        )
