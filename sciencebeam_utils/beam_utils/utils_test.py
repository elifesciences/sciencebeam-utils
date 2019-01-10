import logging

import pytest

import apache_beam as beam
from apache_beam.testing.util import (
    assert_that,
    equal_to
)

from sciencebeam_utils.beam_utils.testing import (
    BeamTest,
    TestPipeline,
    get_counter_value
)

from sciencebeam_utils.beam_utils.utils import (
    MapOrLog,
    TransformAndLog,
    TransformAndCount,
    PreventFusion
)


SOME_VALUE_1 = 'value 1'
SOME_VALUE_2 = 'value 2'
SOME_VALUE_CAUSING_EXCEPTION = 1


def SOME_FN(x):
    return x.upper()


def FN_RAISING_EXCEPTION(_):
    raise RuntimeError('oh dear')


ERROR_COUNT_METRIC_NAME = 'error_count'
COUNT_METRIC_NAME_1 = 'count_1'


def get_logger():
    return logging.getLogger(__name__)


def setup_module():
    logging.basicConfig(level='DEBUG')


@pytest.mark.slow
class TestMapOrLog(BeamTest):
    def test_should_pass_through_return_value_if_no_exception_was_raised(self):
        def fn(x):
            return x.upper()
        with TestPipeline() as p:
            result = (
                p |
                beam.Create([SOME_VALUE_1]) |
                MapOrLog(SOME_FN)
            )
            assert_that(result, equal_to([fn(SOME_VALUE_1)]))

    def test_should_skip_entries_that_cause_an_exception(self):
        with TestPipeline() as p:
            result = (
                p |
                beam.Create([SOME_VALUE_1]) |
                MapOrLog(FN_RAISING_EXCEPTION)
            )
            assert_that(result, equal_to([]))

    def test_should_not_increase_error_metric_counter_if_no_exception_raised(self):
        with TestPipeline() as p:
            _ = (  # noqa: F841
                p |
                beam.Create([SOME_VALUE_1]) |
                MapOrLog(FN_RAISING_EXCEPTION, error_count=ERROR_COUNT_METRIC_NAME)
            )
            assert get_counter_value(p.run(), ERROR_COUNT_METRIC_NAME) == 1

    def test_should_increase_error_metric_counter_if_exception_was_raised(self):
        with TestPipeline() as p:
            _ = (  # noqa: F841
                p |
                beam.Create([SOME_VALUE_1]) |
                MapOrLog(FN_RAISING_EXCEPTION, error_count=ERROR_COUNT_METRIC_NAME)
            )
            assert get_counter_value(p.run(), ERROR_COUNT_METRIC_NAME) == 1


@pytest.mark.slow
class TestTransformAndCount(BeamTest):
    def test_should_not_change_result(self):
        with TestPipeline() as p:
            result = (
                p |
                beam.Create([SOME_VALUE_1.lower()]) |
                TransformAndCount(
                    beam.Map(lambda x: x.upper()),
                    COUNT_METRIC_NAME_1
                )
            )
            assert_that(result, equal_to([SOME_VALUE_1.upper()]))

    def test_should_increase_count_per_item(self):
        with TestPipeline() as p:
            _ = (  # noqa: F841
                p |
                beam.Create([SOME_VALUE_1, SOME_VALUE_2]) |
                TransformAndCount(
                    beam.Map(lambda x: x),
                    COUNT_METRIC_NAME_1
                )
            )
            assert get_counter_value(p.run(), COUNT_METRIC_NAME_1) == 2

    def test_should_increase_count_per_item_using_function(self):
        with TestPipeline() as p:
            _ = (  # noqa: F841
                p |
                beam.Create([SOME_VALUE_1, SOME_VALUE_2]) |
                TransformAndCount(
                    beam.Map(lambda x: x),
                    COUNT_METRIC_NAME_1,
                    len
                )
            )
            assert get_counter_value(p.run(), COUNT_METRIC_NAME_1) == (
                len(SOME_VALUE_1) + len(SOME_VALUE_2)
            )


@pytest.mark.slow
class TestTransformAndLog(BeamTest):
    def test_should_not_change_result(self):
        with TestPipeline() as p:
            result = (
                p |
                beam.Create([SOME_VALUE_1.lower()]) |
                TransformAndLog(
                    beam.Map(lambda x: x.upper())
                )
            )
            assert_that(result, equal_to([SOME_VALUE_1.upper()]))


@pytest.mark.slow
class TestPreventFusion(BeamTest):
    def test_should_not_change_result_with_default_random_key(self):
        with TestPipeline() as p:
            result = (
                p |
                beam.Create([SOME_VALUE_1, SOME_VALUE_2]) |
                PreventFusion()
            )
            assert_that(result, equal_to([SOME_VALUE_1, SOME_VALUE_2]))

    def test_should_not_change_result_with_constant_key(self):
        with TestPipeline() as p:
            result = (
                p |
                beam.Create([SOME_VALUE_1, SOME_VALUE_2]) |
                PreventFusion(lambda _: 1)
            )
            assert_that(result, equal_to([SOME_VALUE_1, SOME_VALUE_2]))
