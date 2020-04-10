from django.test import TestCase
from dictdiffer import diff, patch
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

    def test_save_new_document(self):
        original = {'uid': 100, 'a': 1, 'b': 2}
        doc, is_new, delta = Document.history.save(content=original)

        self.assertTrue(is_new)
        self.assertEqual(doc.uid, '100')
        self.assertEqual(doc.content, original)
        self.assertEqual([], delta)
        self.assertEqual(original, doc.patched_content)

    def test_save_diff_documents(self):
        original = {'uid': 100, 'a': 1, 'b': 2}
        modified = {'uid': 100, 'a': 1, 'b': 3}
        doc, is_new, delta = Document.history.save(content=original)
        self.assertTrue(is_new)
        self.assertEqual([], list(delta))

        another_doc, is_new, delta = Document.history.save(content=modified)

        self.assertFalse(is_new)
        self.assertEqual(doc.uid, another_doc.uid)
        self.assertEqual(doc.id, another_doc.id)
        self.assertEqual(another_doc.content, modified)
        self.assertEqual([('change', 'b', (2, 3))], list(delta))
        self.assertEqual(modified, another_doc.patched_content)


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
