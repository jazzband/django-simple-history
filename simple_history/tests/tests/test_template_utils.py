from datetime import datetime
from typing import Tuple

from django.test import TestCase
from django.utils.dateparse import parse_datetime
from django.utils.safestring import mark_safe

from simple_history.models import ModelChange, ModelDelta
from simple_history.template_utils import HistoricalRecordContextHelper, is_safe_str

from ...tests.models import Choice, Place, Poll, PollWithManyToMany


class HistoricalRecordContextHelperTestCase(TestCase):

    def test__context_for_delta_changes__basic_usage_works_as_expected(self):
        # --- Text and datetimes ---

        old_date = "2021-01-01 12:00:00"
        poll = Poll.objects.create(question="old?", pub_date=parse_datetime(old_date))
        new_date = "2021-01-02 12:00:00"
        poll.question = "new?"
        poll.pub_date = parse_datetime(new_date)
        poll.save()

        new, old = poll.history.all()
        expected_context_list = [
            {
                "field": "Date published",
                "old": old_date,
                "new": new_date,
            },
            {
                "field": "Question",
                "old": "old?",
                "new": "new?",
            },
        ]
        self.assert__context_for_delta_changes__equal(
            Poll, old, new, expected_context_list
        )

        # --- Foreign keys and ints ---

        poll1 = Poll.objects.create(question="1?", pub_date=datetime.now())
        poll2 = Poll.objects.create(question="2?", pub_date=datetime.now())
        choice = Choice.objects.create(poll=poll1, votes=1)
        choice.poll = poll2
        choice.votes = 10
        choice.save()

        new, old = choice.history.all()
        expected_context_list = [
            {
                "field": "Poll",
                "old": f"Poll object ({poll1.pk})",
                "new": f"Poll object ({poll2.pk})",
            },
            {
                "field": "Votes",
                "old": "1",
                "new": "10",
            },
        ]
        self.assert__context_for_delta_changes__equal(
            Choice, old, new, expected_context_list
        )

        # --- M2M objects, text and datetimes (across 3 records) ---

        poll = PollWithManyToMany.objects.create(
            question="old?", pub_date=parse_datetime(old_date)
        )
        poll.question = "new?"
        poll.pub_date = parse_datetime(new_date)
        poll.save()
        place1 = Place.objects.create(name="Place 1")
        place2 = Place.objects.create(name="Place 2")
        poll.places.add(place1, place2)

        newest, _middle, oldest = poll.history.all()
        expected_context_list = [
            # (The dicts should be sorted by the fields' attribute names)
            {
                "field": "Places",
                "old": "[]",
                "new": f"[Place object ({place1.pk}), Place object ({place2.pk})]",
            },
            {
                "field": "Date published",
                "old": old_date,
                "new": new_date,
            },
            {
                "field": "Question",
                "old": "old?",
                "new": "new?",
            },
        ]
        self.assert__context_for_delta_changes__equal(
            PollWithManyToMany, oldest, newest, expected_context_list
        )

    def assert__context_for_delta_changes__equal(
        self, model, old_record, new_record, expected_context_list
    ):
        delta = new_record.diff_against(old_record, foreign_keys_are_objs=True)
        context_helper = HistoricalRecordContextHelper(model, new_record)
        context_list = context_helper.context_for_delta_changes(delta)
        self.assertListEqual(context_list, expected_context_list)

    def test__context_for_delta_changes__with_string_len_around_character_limit(self):
        now = datetime.now()

        def test_context_dict(
            *, initial_question, changed_question, expected_old, expected_new
        ) -> None:
            poll = Poll.objects.create(question=initial_question, pub_date=now)
            poll.question = changed_question
            poll.save()
            new, old = poll.history.all()

            expected_context_dict = {
                "field": "Question",
                "old": expected_old,
                "new": expected_new,
            }
            self.assert__context_for_delta_changes__equal(
                Poll, old, new, [expected_context_dict]
            )
            # Flipping the records should produce the same result (other than also
            # flipping the expected "old" and "new" values, of course)
            expected_context_dict = {
                "field": "Question",
                "old": expected_new,
                "new": expected_old,
            }
            self.assert__context_for_delta_changes__equal(
                Poll, new, old, [expected_context_dict]
            )

        # Check the character limit used in the assertions below
        self.assertEqual(
            HistoricalRecordContextHelper.DEFAULT_MAX_DISPLAYED_DELTA_CHANGE_CHARS, 100
        )

        # Number of characters right on the limit
        test_context_dict(
            initial_question=f"Y{'A' * 99}",
            changed_question=f"W{'A' * 99}",
            expected_old=f"Y{'A' * 99}",
            expected_new=f"W{'A' * 99}",
        )

        # Over the character limit, with various ways that a shared prefix affects how
        # the shortened strings are lined up with each other
        test_context_dict(
            initial_question=f"Y{'A' * 100}",
            changed_question=f"W{'A' * 100}",
            expected_old=f"Y{'A' * 60}[35 chars]AAAAA",
            expected_new=f"W{'A' * 60}[35 chars]AAAAA",
        )
        test_context_dict(
            initial_question=f"{'A' * 100}Y",
            changed_question=f"{'A' * 100}W",
            expected_old=f"AAAAA[13 chars]{'A' * 82}Y",
            expected_new=f"AAAAA[13 chars]{'A' * 82}W",
        )
        test_context_dict(
            initial_question=f"{'A' * 100}Y",
            changed_question=f"{'A' * 199}W",
            expected_old="AAAAA[90 chars]AAAAAY",
            expected_new=f"AAAAA[90 chars]{'A' * 66}[34 chars]AAAAW",
        )
        test_context_dict(
            initial_question=f"{'A' * 50}Y{'E' * 100}",
            changed_question=f"{'A' * 50}W{'E' * 149}",
            expected_old=f"AAAAA[40 chars]AAAAAY{'E' * 60}[35 chars]EEEEE",
            expected_new=f"AAAAA[40 chars]AAAAAW{'E' * 60}[84 chars]EEEEE",
        )
        test_context_dict(
            initial_question=f"{'A' * 50}Y{'E' * 149}",
            changed_question=f"{'A' * 149}W{'E' * 50}",
            expected_old=f"AAAAA[40 chars]AAAAAY{'E' * 60}[84 chars]EEEEE",
            expected_new=f"AAAAA[40 chars]{'A' * 66}[84 chars]EEEEE",
        )

        # Only similar prefixes are detected and lined up;
        # similar parts later in the strings are not
        test_context_dict(
            initial_question=f"{'Y' * 100}{'A' * 50}",
            changed_question=f"{'W' * 100}{'A' * 50}{'H' * 50}",
            expected_old=f"{'Y' * 61}[84 chars]AAAAA",
            expected_new=f"{'W' * 61}[134 chars]HHHHH",
        )

        # Both "old" and "new" under the character limit
        test_context_dict(
            initial_question="A" * 10,
            changed_question="A" * 100,
            expected_old="A" * 10,
            expected_new="A" * 100,
        )
        # "new" just over the limit, but with "old" too short to be shortened
        test_context_dict(
            initial_question="A" * 10,
            changed_question="A" * 101,
            expected_old="A" * 10,
            expected_new=f"{'A' * 71}[25 chars]AAAAA",
        )
        # Both "old" and "new" under the character limit
        test_context_dict(
            initial_question="A" * 99,
            changed_question="A" * 100,
            expected_old="A" * 99,
            expected_new="A" * 100,
        )
        # "new" just over the limit, and "old" long enough to be shortened (which is
        # done even if it's shorter than the character limit)
        test_context_dict(
            initial_question="A" * 99,
            changed_question="A" * 101,
            expected_old=f"AAAAA[13 chars]{'A' * 81}",
            expected_new=f"AAAAA[13 chars]{'A' * 83}",
        )

    def test__context_for_delta_changes__preserves_html_safe_strings(self):
        def get_context_dict_old_and_new(old_value, new_value) -> Tuple[str, str]:
            # The field doesn't really matter, as long as it exists on the model
            # passed to `HistoricalRecordContextHelper`
            change = ModelChange("question", old_value, new_value)
            # (The record args are not (currently) used in the default implementation)
            delta = ModelDelta([change], ["question"], None, None)
            context_helper = HistoricalRecordContextHelper(Poll, None)
            (context_dict,) = context_helper.context_for_delta_changes(delta)
            return context_dict["old"], context_dict["new"]

        # Strings not marked as safe should be escaped
        old_string = "<i>Hey</i>"
        new_string = "<b>Hello</b>"
        old, new = get_context_dict_old_and_new(old_string, new_string)
        self.assertEqual(old, "&lt;i&gt;Hey&lt;/i&gt;")
        self.assertEqual(new, "&lt;b&gt;Hello&lt;/b&gt;")
        # The result should still be marked safe as part of being escaped
        self.assertTrue(is_safe_str(old) and is_safe_str(new))

        # Strings marked as safe should be kept unchanged...
        old_safe_string = mark_safe("<i>Hey</i>")
        new_safe_string = mark_safe("<b>Hello</b>")
        old, new = get_context_dict_old_and_new(old_safe_string, new_safe_string)
        self.assertEqual(old, old_safe_string)
        self.assertEqual(new, new_safe_string)
        self.assertTrue(is_safe_str(old) and is_safe_str(new))

        # ...also if one is safe and the other isn't...
        old_string = "<i>Hey</i>"
        new_safe_string = mark_safe("<b>Hello</b>")
        old, new = get_context_dict_old_and_new(old_string, new_safe_string)
        self.assertEqual(old, "&lt;i&gt;Hey&lt;/i&gt;")
        self.assertEqual(new, new_safe_string)
        self.assertTrue(is_safe_str(old) and is_safe_str(new))

        # ...unless at least one of them is too long, in which case they should both be
        # properly escaped - including mangled tags
        old_safe_string = mark_safe(f"<p><strong>{'A' * 1000}</strong></p>")
        new_safe_string = mark_safe("<p><strong>Hello</strong></p>")
        old, new = get_context_dict_old_and_new(old_safe_string, new_safe_string)
        # (`</strong>` has been mangled)
        expected_old = f"&lt;p&gt;&lt;strong&gt;{'A' * 61}[947 chars]&gt;&lt;/p&gt;"
        self.assertEqual(old, expected_old)
        self.assertEqual(new, "&lt;p&gt;&lt;strong&gt;Hello&lt;/strong&gt;&lt;/p&gt;")
        self.assertTrue(is_safe_str(old) and is_safe_str(new))

        # Unsafe strings inside lists should also be escaped
        old_list = ["Hey", "<i>Hey</i>"]
        new_list = ["<b>Hello</b>", "Hello"]
        old, new = get_context_dict_old_and_new(old_list, new_list)
        self.assertEqual(old, "[Hey, &lt;i&gt;Hey&lt;/i&gt;]")
        self.assertEqual(new, "[&lt;b&gt;Hello&lt;/b&gt;, Hello]")
        self.assertTrue(is_safe_str(old) and is_safe_str(new))

        # Safe strings inside lists should be kept unchanged...
        old_safe_list = [mark_safe("Hey"), mark_safe("<i>Hey</i>")]
        new_safe_list = [mark_safe("<b>Hello</b>"), mark_safe("Hello")]
        old, new = get_context_dict_old_and_new(old_safe_list, new_safe_list)
        self.assertEqual(old, "[Hey, <i>Hey</i>]")
        self.assertEqual(new, "[<b>Hello</b>, Hello]")
        self.assertTrue(is_safe_str(old) and is_safe_str(new))

        # ...but not when not all elements are safe...
        old_half_safe_list = [mark_safe("Hey"), "<i>Hey</i>"]
        new_half_safe_list = [mark_safe("<b>Hello</b>"), "Hello"]
        old, new = get_context_dict_old_and_new(old_half_safe_list, new_half_safe_list)
        self.assertEqual(old, "[Hey, &lt;i&gt;Hey&lt;/i&gt;]")
        self.assertEqual(new, "[&lt;b&gt;Hello&lt;/b&gt;, Hello]")
        self.assertTrue(is_safe_str(old) and is_safe_str(new))

        # ...and also not when some of the elements are too long
        old_safe_list = [mark_safe("Hey"), mark_safe(f"<i>{'A' * 1000}</i>")]
        new_safe_list = [mark_safe("<b>Hello</b>"), mark_safe(f"{'B' * 1000}")]
        old, new = get_context_dict_old_and_new(old_safe_list, new_safe_list)
        self.assertEqual(old, f"[Hey, &lt;i&gt;{'A' * 53}[947 chars]&lt;/i&gt;]")
        self.assertEqual(new, f"[&lt;b&gt;Hello&lt;/b&gt;, {'B' * 47}[949 chars]BBBB]")
        self.assertTrue(is_safe_str(old) and is_safe_str(new))

        # HTML tags inside too long strings should be properly escaped - including
        # mangled tags
        old_safe_list = [mark_safe(f"<h1><i>{'A' * 1000}</i></h1>")]
        new_safe_list = [mark_safe(f"<strong>{'B' * 1000}</strong>")]
        old, new = get_context_dict_old_and_new(old_safe_list, new_safe_list)
        # (Tags have been mangled at the end of the strings)
        self.assertEqual(old, f"[&lt;h1&gt;&lt;i&gt;{'A' * 55}[950 chars]/h1&gt;]")
        self.assertEqual(new, f"[&lt;strong&gt;{'B' * 54}[951 chars]ong&gt;]")
        self.assertTrue(is_safe_str(old) and is_safe_str(new))
