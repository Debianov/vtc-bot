import pytest

from bot.objects.text import *

good_act_user_texts = [
	">владимир",
	"-анна",
	"+константинополь",
	"++++++с"
]

bad_act_user_texts = [
	"2ch",
	"&увебе",
	"?:№)рсчс",
	"увс-оп",
	"пиксель>"
]

good_int_and_str_user_texts = [
	"123214142",
	"sd324",
	"N\n"
]

bad_int_and_str_user_texts = [
	"sad",
	"Не \n акупает",
]

good_int_user_texts = [		
	"124234",
	"67834345"
]

bad_int_user_texts = [
	"1sdf",
	"hgfk43",
	"пиксель>"
]

bad_mention_user_texts = [
	"<@1241124sd>",
	"<#74",
	"#123323",
	"@124>"
]

good_channel_mention_user_texts = [
	"<#12414>",
	"<#74>"
]

bad_channel_mention_user_texts = [
	"<#7412e334>"
]

good_user_mention_user_texts = [
	"<@12414>",
	"<@74>"
]

bad_user_mention_user_texts = [
	"<@74sdg>",
]

@pytest.mark.parametrize(
	"user_text", good_act_user_texts
)
def test_good_act_text_definition(user_text) -> None:
	ActText(user_text).checkText()

@pytest.mark.parametrize(
	"user_text", bad_act_user_texts
)
def test_bad_act_text_definition(user_text) -> None:
	with pytest.raises(WrongActSignal):
		ActText(user_text).checkText()

@pytest.mark.parametrize(
	"user_text", 
	bad_act_user_texts + good_act_user_texts + good_int_and_str_user_texts
)
def test_dummy_text_definition(user_text) -> None:
	DummyText(user_text).checkText()

@pytest.mark.parametrize(
	"user_text", 
	bad_act_user_texts + good_act_user_texts + good_int_and_str_user_texts + bad_mention_user_texts
)
def test_good_str_or_int_text_definition(user_text) -> None:
	StrOrIntText(user_text).checkText()

@pytest.mark.parametrize(
	"user_text",
	good_channel_mention_user_texts + good_user_mention_user_texts + bad_int_and_str_user_texts
)
def test_bad_str_or_int_text_definition(user_text) -> None:
	with pytest.raises(WrongTextTypeSignal):
		StrOrIntText(user_text).checkText()

@pytest.mark.parametrize(
	"user_text", 
	good_int_user_texts
)
def test_good_int_text_definition(user_text) -> None:
	IntText(user_text).checkText()

@pytest.mark.parametrize(
	"user_text", 
	bad_int_user_texts
)
def test_bad_int_text_definition(user_text) -> None:
	with pytest.raises(WrongTextTypeSignal):
		IntText(user_text).checkText()

@pytest.mark.parametrize(
	"user_text", 
	good_channel_mention_user_texts + good_user_mention_user_texts
)
def test_good_mention_text_definition(user_text) -> None:
	instance = MentionText(user_text)
	instance.checkText()
	instance.processText()
	assert instance.getText() == user_text.removeprefix("<").removesuffix(">")

@pytest.mark.parametrize(
	"user_text", 
	bad_mention_user_texts
)
def test_bad_mention_text_definition(user_text) -> None:
	instance = MentionText(user_text)
	with pytest.raises(WrongTextTypeSignal):
		instance.checkText()

@pytest.mark.parametrize(
	"user_text", 
	good_channel_mention_user_texts
)
def test_good_channel_mention_text_definition(user_text) -> None:
	instance = ChannelMentionText(user_text)
	instance.checkText()
	instance.processText()
	assert instance.getText() == user_text.removeprefix("<").removesuffix(">")

@pytest.mark.parametrize(
	"user_text", 
	bad_channel_mention_user_texts + good_user_mention_user_texts + bad_mention_user_texts
)
def test_bad_channel_mention_text_definition(user_text) -> None:
	instance = ChannelMentionText(user_text)
	with pytest.raises(WrongTextTypeSignal):
		instance.checkText()

@pytest.mark.parametrize(
	"user_text", 
	good_user_mention_user_texts
)
def test_good_user_mention_text_definition(user_text) -> None:
	instance = UserMentionText(user_text)
	instance.checkText()
	instance.processText()
	assert instance.getText() == user_text.removeprefix("<").removesuffix(">")

@pytest.mark.parametrize(
	"user_text", 
	bad_user_mention_user_texts + good_channel_mention_user_texts + bad_mention_user_texts
)
def test_bad_user_mention_text_definition(user_text) -> None:
	instance = UserMentionText(user_text)
	with pytest.raises(WrongTextTypeSignal):
		instance.checkText()