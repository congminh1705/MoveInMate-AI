import pytest

from src.services.public_speech import PublicSpeechSegments, normalize_speech_text, speech_text


@pytest.mark.parametrize("text,expected", [
    ("BQL, bql! (BqL).", "ban quản lí, ban quản lí! (ban quản lí)."),
    ("ABQL BQLA BQL1 1BQL BQL_name đBQL BQLđ", "ABQL BQLA BQL1 1BQL BQL_name đBQL BQLđ"),
    ("BQL/BQL: cư dân", "ban quản lí/ban quản lí: cư dân"),
    ("ban quản lí", "ban quản lí"),
])
def test_normalize_standalone_abbreviation(text, expected):
    assert normalize_speech_text(text) == expected
    assert normalize_speech_text(expected) == expected


def test_speech_cleanup_normalizes_only_spoken_content():
    assert speech_text("**BQL** [bql](https://example.test) `BQL`\n```BQL``` 123456789012") == "ban quản lí ban quản lí ban quản lí"


def test_stream_normalizes_abbreviation_split_across_deltas():
    stream = PublicSpeechSegments()
    assert stream.append("Liên hệ B") == []
    assert stream.append("Q") == []
    segments = stream.append("L.")
    assert [segment["text"] for segment in segments] == ["Liên hệ ban quản lí."]
    assert stream.spoken == len("Liên hệ ban quản lí.")


def test_stream_budget_counts_expanded_text():
    stream = PublicSpeechSegments()
    segments = stream.append("BQL " * 1500, final=True)
    assert sum(len(segment["text"]) for segment in segments) == stream.spoken == 5000
    assert stream.truncated


def test_following_speech_is_available_without_waiting_for_a_long_paragraph():
    stream = PublicSpeechSegments()
    first = stream.append("Xin chào cư dân. ")
    assert len(first) == 1
    following = "Bạn kiểm tra lại thông tin căn hộ và tên người đăng ký trước khi gửi để ban quản lí có thể tiếp nhận đúng hồ sơ của bạn. "
    assert 120 <= len(following) < 350
    segments = stream.append(following)
    assert [segment["text"] for segment in segments] == [following.strip()]
    assert stream.append("", final=True) == []


def test_short_stream_chunks_preserve_words_order_and_the_total_budget():
    text = "Thông tin cư dân cần được đối chiếu rõ ràng trước khi gửi hồ sơ. " * 40
    stream = PublicSpeechSegments()
    segments = []
    for offset in range(0, len(text), 7):
        segments.extend(stream.append(text[offset:offset + 7]))
    segments.extend(stream.append("", final=True))
    assert " ".join(segment["text"] for segment in segments) == speech_text(text)
    assert len(segments[0]["text"]) <= 120
    assert all(len(segment["text"]) <= 320 for segment in segments[1:])
    assert [segment["index"] for segment in segments] == list(range(1, len(segments) + 1))
    assert not stream.truncated


def test_a_complete_short_following_sentence_is_released_without_waiting_for_more_text():
    stream = PublicSpeechSegments()
    assert stream.append("Xin chào cư dân. ")
    following = "Bạn kiểm tra thông tin căn hộ. "
    assert len(following) < 120
    assert [segment["text"] for segment in stream.append(following)] == [following.strip()]
    assert stream.append("", final=True) == []


def test_ready_following_sentences_are_batched_without_delaying_the_first_sentence():
    stream = PublicSpeechSegments()
    text = "Xin chào cư dân. Bạn kiểm tra thông tin căn hộ. Sau đó xác nhận hồ sơ. "
    segments = stream.append(text)
    assert [segment["text"] for segment in segments] == [
        "Xin chào cư dân.", "Bạn kiểm tra thông tin căn hộ. Sau đó xác nhận hồ sơ.",
    ]
    assert " ".join(segment["text"] for segment in segments) == speech_text(text)
    assert stream.append("", final=True) == []
