import mock
from django.test import TestCase
from django.utils import timezone
from dictdiffer import diff, patch
from dateutil.relativedelta import *
from leoparser.models import Document, RemovableHistoryDocument, DocDelta


class TestDictdiffer(TestCase):

    def test_no_changes(self):
        original = {'a': 1, 'b': 2}
        modified = {'a': 1, 'b': 2}
        delta = list(diff(original, modified))
        new = patch(delta, original)
        self.assertEqual(new, modified)
        new = patch(delta, modified)
        self.assertEqual(new, modified)

    def test_update_value(self):
        original = {'a': 1, 'b': 2}
        modified = {'a': 1, 'b': 4}
        delta = list(diff(original, modified))
        new = patch(delta, original)
        self.assertEqual(new, modified)
        new = patch(delta, modified)
        self.assertEqual(new, modified)

    def test_add_value(self):
        original = {'a': 1, 'b': 2}
        modified = {'a': 1, 'b': 2, 'c': 3}
        delta = list(diff(original, modified))
        new = patch(delta, original)
        self.assertEqual(new, modified)
        new = patch(delta, modified)
        self.assertEqual(new, modified)

    def test_remove_value(self):
        original = {'a': 1, 'b': 2, 'c': 3}
        modified = {'a': 1, 'b': 2}
        delta = list(diff(original, modified))
        new = patch(delta, original)
        self.assertEqual(new, modified)

        with self.assertRaises(KeyError) as cm:
            patch(delta, modified)
        self.assertEqual(cm.exception.args[0], 'c')


class TestDocumentWithoutSaving(TestCase):

    def test_update_value(self):
        original = {'a': 1, 'b': 2}
        modified = {'a': 1, 'b': 4}
        doc = Document()
        doc.content = original
        self.assertEqual(doc.content, original)
        self.assertEqual([], list(doc.delta))
        self.assertEqual(original, doc.patched_content)

        doc.content = modified
        self.assertEqual(doc.content, modified)
        self.assertEqual([], list(doc.delta))
        self.assertEqual(modified, doc.patched_content)

    def test_add_value(self):
        original = {'a': 1, 'b': 2}
        modified = {'a': 1, 'b': 2, 'c': 3}
        doc = Document()
        doc.content = original
        self.assertEqual(doc.content, original)
        self.assertEqual([], list(doc.delta))
        self.assertEqual(original, doc.patched_content)

        doc.content = modified
        self.assertEqual(doc.content, modified)
        self.assertEqual([], list(doc.delta))
        self.assertEqual(modified, doc.patched_content)

    def test_remove_value(self):
        original = {'a': 1, 'b': 2}
        modified = {'a': 1}
        doc = Document()
        doc.content = original
        self.assertEqual(doc.content, original)
        self.assertEqual([], list(doc.delta))
        self.assertEqual(original, doc.patched_content)

        doc.content = modified
        self.assertEqual(doc.content, modified)
        self.assertEqual([], list(doc.delta))
        self.assertEqual(modified, doc.patched_content)


class TestDocumentAfterSaving(TestCase):

    def test_update_value(self):
        original = {'a': 1, 'b': 2}
        modified = {'a': 1, 'b': 4}
        modified_again = {'a': 2, 'b': 4}
        doc = Document()
        doc.content = original
        doc.save()

        doc.content = modified
        self.assertEqual(doc.content, modified)
        self.assertEqual([('change', 'b', (2, 4))], list(doc.delta))
        self.assertEqual(modified, doc.patched_content)

        doc.content = modified_again
        self.assertEqual(doc.content, modified_again)
        self.assertEqual([('change', 'a', (1, 2)), ('change', 'b', (2, 4))], list(doc.delta))
        self.assertEqual(modified_again, doc.patched_content)

    def test_add_value(self):
        original = {'a': 1, 'b': 2}
        modified = {'a': 1, 'b': 2, 'c': 3}
        modified_again = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
        doc = Document()
        doc.content = original
        doc.save()

        doc.content = modified
        self.assertEqual(doc.content, modified)
        self.assertEqual([('add', '', [('c', 3)])], list(doc.delta))
        self.assertEqual(modified, doc.patched_content)

        doc.content = modified_again
        self.assertEqual(doc.content, modified_again)
        self.assertEqual([('add', '', [('c', 3), ('d', 4)])], list(doc.delta))
        self.assertEqual(modified_again, doc.patched_content)

    def test_remove_value(self):
        original = {'a': 1, 'b': 2}
        modified = {'a': 1}
        modified_again = {}
        doc = Document()
        doc.content = original
        doc.save()

        doc.content = modified
        self.assertEqual(doc.content, modified)
        self.assertEqual([], list(doc.delta))
        self.assertEqual(original, doc.patched_content)

        doc.content = modified_again
        self.assertEqual(doc.content, modified_again)
        self.assertEqual([], list(doc.delta))
        self.assertEqual(original, doc.patched_content)


class TestDocumentAfterDupleSaving(TestCase):

    def test_update_value(self):
        original = {'a': 1, 'b': 2}
        modified = {'a': 1, 'b': 4}
        modified_again = {'a': 2, 'b': 4}
        doc = Document()
        doc.content = original
        doc.save()

        doc.content = modified
        self.assertEqual(doc.content, modified)
        self.assertEqual([('change', 'b', (2, 4))], list(doc.delta))
        self.assertEqual(modified, doc.patched_content)
        doc.save()

        doc.content = modified_again
        self.assertEqual(doc.content, modified_again)
        self.assertEqual([('change', 'a', (1, 2))], list(doc.delta))
        self.assertEqual(modified_again, doc.patched_content)

    def test_add_value(self):
        original = {'a': 1, 'b': 2}
        modified = {'a': 1, 'b': 2, 'c': 3}
        modified_again = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
        doc = Document()
        doc.content = original
        doc.save()

        doc.content = modified
        self.assertEqual(doc.content, modified)
        self.assertEqual([('add', '', [('c', 3)])], list(doc.delta))
        self.assertEqual(modified, doc.patched_content)
        doc.save()

        doc.content = modified_again
        self.assertEqual(doc.content, modified_again)
        self.assertEqual([('add', '', [('d', 4)])], list(doc.delta))
        self.assertEqual(modified_again, doc.patched_content)

    def test_remove_value(self):
        original = {'a': 1, 'b': 2}
        modified = {'a': 1}
        modified_again = {}
        doc = Document()
        doc.content = original
        doc.save()

        doc.content = modified
        self.assertEqual(doc.content, modified)
        self.assertEqual([], list(doc.delta))
        self.assertEqual(original, doc.patched_content)
        doc.save()

        doc.content = modified_again
        self.assertEqual(doc.content, modified_again)
        self.assertEqual([], list(doc.delta))
        self.assertEqual(original, doc.patched_content)


class TestRemovableHistoryDocumentWithoutSaving(TestCase):

    def test_remove_value(self):
        original = {'a': 1, 'b': 2}
        modified = {'a': 1}
        doc = RemovableHistoryDocument()
        doc.content = original
        self.assertEqual(doc.content, original)
        self.assertEqual([], list(doc.delta))
        self.assertEqual(original, doc.patched_content)

        doc.content = modified
        self.assertEqual(doc.content, modified)
        self.assertEqual([], list(doc.delta))
        self.assertEqual(modified, doc.patched_content)


class TestRemovableHistoryDocumentAfterSaving(TestCase):

    def test_remove_value(self):
        original = {'a': 1, 'b': 2}
        modified = {'a': 1}
        modified_again = {}
        doc = RemovableHistoryDocument()
        doc.content = original
        doc.save()

        doc.content = modified
        self.assertEqual(doc.content, modified)
        self.assertEqual([('remove', '', [('b', 2)])], list(doc.delta))
        self.assertEqual(modified, doc.patched_content)

        doc.content = modified_again
        self.assertEqual(doc.content, modified_again)
        self.assertEqual([('remove', '', [('a', 1), ('b', 2)])], list(doc.delta))
        self.assertEqual(modified_again, doc.patched_content)


class TestRemovableHistoryDocumentAfterDupleSaving(TestCase):

    def test_remove_value(self):
        original = {'a': 1, 'b': 2}
        modified = {'a': 1}
        modified_again = {}
        doc = RemovableHistoryDocument()
        doc.content = original
        doc.save()

        doc.content = modified
        self.assertEqual(doc.content, modified)
        self.assertEqual([('remove', '', [('b', 2)])], list(doc.delta))
        self.assertEqual(modified, doc.patched_content)
        doc.save()

        doc.content = modified_again
        self.assertEqual(doc.content, modified_again)
        self.assertEqual([('remove', '', [('a', 1)])], list(doc.delta))
        self.assertEqual(modified_again, doc.patched_content)


class TestBaseModelBehaviour(TestCase):

    def test_constructor(self):
        original = {'a': 1, 'b': 2}
        modified = {'a': 1, 'b': 2, 'c': 3}
        doc = Document(content=original)
        doc.save()
        doc.content = modified

        doc.content = modified
        self.assertEqual(doc.content, modified)
        self.assertEqual([('add', '', [('c', 3)])], list(doc.delta))
        self.assertEqual(modified, doc.patched_content)

    def test_create(self):
        original = {'a': 1, 'b': 2}
        modified = {'a': 1, 'b': 2, 'c': 3}
        doc = Document.objects.create(content=original)
        doc.content = modified

        doc.content = modified
        self.assertEqual(doc.content, modified)
        self.assertEqual([('add', '', [('c', 3)])], list(doc.delta))
        self.assertEqual(modified, doc.patched_content)

    def test_get_or_create(self):
        original = {'a': 1, 'b': 2}
        modified = {'a': 1, 'b': 2, 'c': 3}
        doc, created = Document.objects.get_or_create(content=original)
        self.assertTrue(created)
        doc.content = modified

        doc.content = modified
        self.assertEqual(doc.content, modified)
        self.assertEqual([('add', '', [('c', 3)])], list(doc.delta))
        self.assertEqual(modified, doc.patched_content)

        doc, created = Document.objects.get_or_create(content=original)
        self.assertFalse(created)
        doc.content = modified

        doc.content = modified
        self.assertEqual(doc.content, modified)
        self.assertEqual([('add', '', [('c', 3)])], list(doc.delta))
        self.assertEqual(modified, doc.patched_content)


class TestHistoryManagerWithDataUid(TestCase):

    def setUp(self):
        self.original = {'uid': 1, 'a': 1}
        self.modified = {'uid': 1, 'a': 2}

    def test_save_new_document(self):
        doc, is_new, delta = Document.history.save(content=self.original)

        self.assertTrue(is_new)
        self.assertEqual(doc.uid, '1')
        self.assertEqual(doc.content, self.original)
        self.assertEqual([], delta)
        self.assertEqual(self.original, doc.patched_content)

    def test_save_diff_documents(self):
        doc, is_new, delta = Document.history.save(content=self.original)
        self.assertTrue(is_new)
        self.assertEqual([], list(delta))

        another_doc, is_new, delta = Document.history.save(content=self.modified)

        self.assertFalse(is_new)
        self.assertEqual(doc.uid, another_doc.uid)
        self.assertEqual(doc.id, another_doc.id)
        self.assertEqual(another_doc.content, self.modified)
        self.assertEqual([('change', 'a', (1, 2))], list(delta))
        self.assertEqual(self.modified, another_doc.patched_content)

    def _create_doc_with_delta_in_the_past(self, *, years=0, months=0, weeks=0, days=0, hours=0, minutes=0, seconds=0):
        Document.history.save(content=self.original)
        today = timezone.now()
        last_datetime = today - relativedelta(years=years, months=months, weeks=weeks, days=days,
                                              hours=hours, minutes=minutes, seconds=seconds)
        print(last_datetime)
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=last_datetime)):
            doc, _, _ = Document.history.save(content=self.modified)

        return doc

    def test_return_history_for_last_year_negative(self):
        doc = self._create_doc_with_delta_in_the_past(years=1, days=1)

        delta_set = doc.delta_set.all()
        self.assertEqual(1, len(delta_set))

        year_history = doc.get_year_history()
        self.assertEqual(1, len(year_history))

    def test_return_history_for_last_year_positive(self):
        doc = self._create_doc_with_delta_in_the_past(years=1)

        delta_set = doc.delta_set.all()
        self.assertEqual(1, len(delta_set))

        year_history = doc.get_year_history()
        self.assertEqual(2, len(year_history))

    def test_return_history_for_last_month_negative(self):
        doc = self._create_doc_with_delta_in_the_past(months=1, days=1)

        delta_set = doc.delta_set.all()
        self.assertEqual(1, len(delta_set))

        month_history = doc.get_month_history()
        self.assertEqual(1, len(month_history))

    def test_return_history_for_last_month_positive(self):
        doc = self._create_doc_with_delta_in_the_past(months=1)

        delta_set = doc.delta_set.all()
        self.assertEqual(1, len(delta_set))

        month_history = doc.get_month_history()
        self.assertEqual(2, len(month_history))

    def test_return_history_for_last_week_negative(self):
        doc = self._create_doc_with_delta_in_the_past(weeks=1, days=1)

        delta_set = doc.delta_set.all()
        self.assertEqual(1, len(delta_set))

        week_history = doc.get_week_history()
        self.assertEqual(1, len(week_history))

    def test_return_history_for_last_week_positive(self):
        doc = self._create_doc_with_delta_in_the_past(weeks=1)

        delta_set = doc.delta_set.all()
        self.assertEqual(1, len(delta_set))

        week_history = doc.get_week_history()
        self.assertEqual(2, len(week_history))

    def test_return_history_for_last_day_negative(self):
        doc = self._create_doc_with_delta_in_the_past(hours=24)

        delta_set = doc.delta_set.all()
        self.assertEqual(1, len(delta_set))

        day_history = doc.get_day_history()
        self.assertEqual(1, len(day_history))

    def test_return_history_for_last_day_positive(self):
        doc = self._create_doc_with_delta_in_the_past(hours=23, minutes=59, seconds=59)

        delta_set = doc.delta_set.all()
        self.assertEqual(1, len(delta_set))

        day_history = doc.get_day_history()
        self.assertEqual(2, len(day_history))

    def test_fetch_n_last_results(self):
        doc = self._create_doc_with_delta_in_the_past()

        self.assertEqual(0, len(doc.get_history(0)))
        self.assertEqual(1, len(doc.get_history(1)))
        self.assertEqual(2, len(doc.get_history(2)))
        self.assertEqual(2, len(doc.get_history()))
        self.assertEqual(1, len(doc.get_history('1')))

        with self.assertRaises((TypeError,),) as err:
            doc.get_history('invalid number')
        self.assertIn('Amount of history items must be integer representable', err.exception.args[0])


class TestHistoryManagerWithoutDataUid(TestCase):

    def test_save_new_document(self):
        original = {'a': 1, 'b': 2}
        doc, is_new, delta = Document.history.save(content=original)

        self.assertTrue(is_new)
        self.assertRegex(doc.uid, r'[0-9a-f]{32}')
        self.assertEqual(doc.content, original)
        self.assertEqual([], list(delta))
        self.assertEqual(original, doc.patched_content)

    def test_save_equal_documents(self):
        original = {'a': 1, 'b': 2}
        modified = {'a': 1, 'b': 2}
        doc, is_new, delta = Document.history.save(content=original)
        self.assertTrue(is_new)

        another_doc, is_new, delta = Document.history.save(content=modified)

        self.assertTrue(is_new)
        self.assertNotEqual(doc.uid, another_doc.uid)
        self.assertEqual(another_doc.content, modified)
        self.assertEqual([], list(delta))
        self.assertEqual(modified, another_doc.patched_content)


class TestSignalAutoSaveDelta(TestCase):

    def test_auto_creating_docdelte_object(self):
        original = {'uid': 1, 'a': 1, 'b': 2}
        modified = {'uid': 1, 'a': 1, 'b': 4}
        Document.history.save(content=original)
        Document.history.save(content=modified)

        delta_set = DocDelta.objects.all()
        self.assertEqual(1, len(delta_set))
        self.assertEqual([['change', 'b', [2, 4]]], delta_set[0].delta)


class TestRetrieveDocumentHistory(TestCase):

    def setUp(self):
        self.doc_versions = [
            {'uid': 1, 'a': 1, 'b': 2},
            {'uid': 1, 'a': 1, 'b': 4},
            {'uid': 1, 'a': 1, 'b': 2, 'c': 3},
            {'uid': 1, 'a': 1}  # won't be counted for Document
        ]

    def test_retrieving_doc_history(self):

        doc = None
        for version in self.doc_versions:
            doc, is_new, delta = Document.history.save(content=version)

        history = doc.get_history()

        self.assertEqual(3, len(history))

        self.assertEqual(self.doc_versions[2], history[0])
        self.assertEqual(self.doc_versions[1], history[1])
        self.assertEqual(self.doc_versions[0], history[2])

    def test_retrieving_removable_doc_history(self):

        doc = None
        for version in self.doc_versions:
            doc, is_new, delta = RemovableHistoryDocument.history.save(content=version)

        history = doc.get_history()

        self.assertEqual(4, len(history))
        self.assertEqual(self.doc_versions[3], history[0])
        self.assertEqual(self.doc_versions[2], history[1])
        self.assertEqual(self.doc_versions[1], history[2])
        self.assertEqual(self.doc_versions[0], history[3])



