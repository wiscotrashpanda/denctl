"""Property-based tests for the launchctl helper module.

These tests use Hypothesis to verify universal properties across all inputs
for the launchctl validator functions.
"""

from hypothesis import given, settings, strategies as st

from den.launchctl_validator import (
    validate_task_name,
    validate_interval,
    validate_hour,
    validate_minute,
)
from den.plist_generator import TaskConfig, generate_plist, parse_plist


# Strategies for generating test data
valid_task_name_chars = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-",
    min_size=1,
)

# Characters that should be rejected in task names
invalid_task_name_chars = st.text(
    alphabet=" /\\!@#$%^&*()+=[]{}|;:'\",.<>?`~",
    min_size=1,
)


@settings(max_examples=100)
@given(name=valid_task_name_chars)
def test_property_valid_task_names_accepted(name: str):
    """**Feature: launchctl-helper, Property 7: Task Name Character Validation**

    *For any* string containing only alphanumeric characters, hyphens, and
    underscores, the validator should accept it.

    **Validates: Requirements 6.2**
    """
    is_valid, error_msg = validate_task_name(name)
    assert is_valid is True, f"Valid task name '{name}' was rejected: {error_msg}"
    assert error_msg == ""


@settings(max_examples=100)
@given(name=invalid_task_name_chars)
def test_property_invalid_task_names_rejected(name: str):
    """**Feature: launchctl-helper, Property 7: Task Name Character Validation**

    *For any* string containing spaces, slashes, or special characters
    (other than hyphens and underscores), the task name validator should reject it.

    **Validates: Requirements 6.2**
    """
    is_valid, error_msg = validate_task_name(name)
    assert is_valid is False, f"Invalid task name '{name}' was accepted"
    assert error_msg != ""


@settings(max_examples=100)
@given(seconds=st.integers(max_value=0))
def test_property_non_positive_intervals_rejected(seconds: int):
    """**Feature: launchctl-helper, Property 8: Interval Validation**

    *For any* integer less than or equal to zero, the interval validator
    should reject it.

    **Validates: Requirements 6.4**
    """
    is_valid, error_msg = validate_interval(seconds)
    assert is_valid is False, f"Non-positive interval {seconds} was accepted"
    assert error_msg != ""


@settings(max_examples=100)
@given(seconds=st.integers(min_value=1))
def test_property_positive_intervals_accepted(seconds: int):
    """**Feature: launchctl-helper, Property 8: Interval Validation**

    *For any* positive integer, the interval validator should accept it.

    **Validates: Requirements 6.4**
    """
    is_valid, error_msg = validate_interval(seconds)
    assert is_valid is True, f"Positive interval {seconds} was rejected: {error_msg}"
    assert error_msg == ""


@settings(max_examples=100)
@given(hour=st.integers(min_value=0, max_value=23))
def test_property_valid_hours_accepted(hour: int):
    """**Feature: launchctl-helper, Property 9: Hour Validation**

    *For any* integer in the range 0-23, the hour validator should accept it.

    **Validates: Requirements 6.5**
    """
    is_valid, error_msg = validate_hour(hour)
    assert is_valid is True, f"Valid hour {hour} was rejected: {error_msg}"
    assert error_msg == ""


@settings(max_examples=100)
@given(hour=st.integers().filter(lambda x: x < 0 or x > 23))
def test_property_invalid_hours_rejected(hour: int):
    """**Feature: launchctl-helper, Property 9: Hour Validation**

    *For any* integer outside the range 0-23, the hour validator should reject it.

    **Validates: Requirements 6.5**
    """
    is_valid, error_msg = validate_hour(hour)
    assert is_valid is False, f"Invalid hour {hour} was accepted"
    assert error_msg != ""


@settings(max_examples=100)
@given(minute=st.integers(min_value=0, max_value=59))
def test_property_valid_minutes_accepted(minute: int):
    """**Feature: launchctl-helper, Property 10: Minute Validation**

    *For any* integer in the range 0-59, the minute validator should accept it.

    **Validates: Requirements 6.6**
    """
    is_valid, error_msg = validate_minute(minute)
    assert is_valid is True, f"Valid minute {minute} was rejected: {error_msg}"
    assert error_msg == ""


@settings(max_examples=100)
@given(minute=st.integers().filter(lambda x: x < 0 or x > 59))
def test_property_invalid_minutes_rejected(minute: int):
    """**Feature: launchctl-helper, Property 10: Minute Validation**

    *For any* integer outside the range 0-59, the minute validator should reject it.

    **Validates: Requirements 6.6**
    """
    is_valid, error_msg = validate_minute(minute)
    assert is_valid is False, f"Invalid minute {minute} was accepted"
    assert error_msg != ""


# Strategies for plist generator tests
valid_domain_strategy = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789.",
    min_size=3,
    max_size=50,
).filter(lambda x: not x.startswith(".") and not x.endswith(".") and ".." not in x)

valid_task_name_strategy = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-",
    min_size=1,
    max_size=50,
)

# Strategy for non-empty program arguments (printable characters only, no control chars)
# Plist XML cannot contain control characters
printable_text = st.text(
    alphabet=st.characters(
        whitelist_categories=("L", "N", "P", "S", "Zs"),
        blacklist_characters="\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0e\x0f"
        "\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f",
    ),
    min_size=1,
    max_size=100,
).filter(lambda x: x.strip())

valid_program_arguments = st.lists(
    printable_text,
    min_size=1,
    max_size=10,
)

# Strategy for valid TaskConfig with interval scheduling
interval_task_config_strategy = st.builds(
    TaskConfig,
    label=st.tuples(valid_domain_strategy, valid_task_name_strategy).map(
        lambda t: f"{t[0]}.{t[1]}"
    ),
    program_arguments=valid_program_arguments,
    start_interval=st.integers(min_value=1, max_value=86400),
    start_calendar_hour=st.none(),
    start_calendar_minute=st.none(),
    run_at_load=st.booleans(),
)

# Strategy for valid TaskConfig with calendar scheduling
calendar_task_config_strategy = st.builds(
    TaskConfig,
    label=st.tuples(valid_domain_strategy, valid_task_name_strategy).map(
        lambda t: f"{t[0]}.{t[1]}"
    ),
    program_arguments=valid_program_arguments,
    start_interval=st.none(),
    start_calendar_hour=st.integers(min_value=0, max_value=23),
    start_calendar_minute=st.integers(min_value=0, max_value=59),
    run_at_load=st.booleans(),
)

# Combined strategy for any valid TaskConfig
valid_task_config_strategy = st.one_of(
    interval_task_config_strategy,
    calendar_task_config_strategy,
)


@settings(max_examples=100)
@given(config=valid_task_config_strategy)
def test_property_plist_round_trip(config: TaskConfig):
    """**Feature: launchctl-helper, Property 1: Plist Round-Trip Consistency**

    *For any* valid TaskConfig, generating a plist XML string and then parsing
    it back should produce an equivalent TaskConfig object.

    **Validates: Requirements 5.7**
    """
    xml_content = generate_plist(config)
    parsed_config = parse_plist(xml_content)

    assert parsed_config.label == config.label
    assert parsed_config.program_arguments == config.program_arguments
    assert parsed_config.start_interval == config.start_interval
    assert parsed_config.start_calendar_hour == config.start_calendar_hour
    assert parsed_config.start_calendar_minute == config.start_calendar_minute
    assert parsed_config.run_at_load == config.run_at_load


@settings(max_examples=100)
@given(domain=valid_domain_strategy, task_name=valid_task_name_strategy)
def test_property_label_matches_configuration(domain: str, task_name: str):
    """**Feature: launchctl-helper, Property 2: Label Matches Configuration**

    *For any* valid domain string and task name, the generated plist's Label
    value should equal {domain}.{task}.

    **Validates: Requirements 5.2**
    """
    expected_label = f"{domain}.{task_name}"
    config = TaskConfig(
        label=expected_label,
        program_arguments=["/bin/echo", "test"],
        start_interval=60,
    )

    xml_content = generate_plist(config)
    parsed_config = parse_plist(xml_content)

    assert parsed_config.label == expected_label


@settings(max_examples=100)
@given(program_args=valid_program_arguments)
def test_property_command_arguments_preserved(program_args: list[str]):
    """**Feature: launchctl-helper, Property 3: Command Arguments Preserved**

    *For any* valid TaskConfig with a non-empty program_arguments list, the
    generated plist should contain all command arguments in the same order.

    **Validates: Requirements 5.3**
    """
    config = TaskConfig(
        label="com.test.task",
        program_arguments=program_args,
        start_interval=60,
    )

    xml_content = generate_plist(config)
    parsed_config = parse_plist(xml_content)

    assert parsed_config.program_arguments == program_args


@settings(max_examples=100)
@given(config=valid_task_config_strategy)
def test_property_schedule_configuration_preserved(config: TaskConfig):
    """**Feature: launchctl-helper, Property 4: Schedule Configuration Preserved**

    *For any* valid TaskConfig with either start_interval set or
    start_calendar_hour/start_calendar_minute set, the generated plist should
    contain the corresponding scheduling keys with the exact values specified.

    **Validates: Requirements 5.4, 5.5**
    """
    xml_content = generate_plist(config)
    parsed_config = parse_plist(xml_content)

    # Verify interval scheduling is preserved
    if config.start_interval is not None:
        assert parsed_config.start_interval == config.start_interval
        assert parsed_config.start_calendar_hour is None
        assert parsed_config.start_calendar_minute is None

    # Verify calendar scheduling is preserved
    if (
        config.start_calendar_hour is not None
        and config.start_calendar_minute is not None
    ):
        assert parsed_config.start_calendar_hour == config.start_calendar_hour
        assert parsed_config.start_calendar_minute == config.start_calendar_minute
        assert parsed_config.start_interval is None
