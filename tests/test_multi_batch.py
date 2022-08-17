from unittest import TestCase, mock
from fielder_backend_utils.firebase import FirebaseHelper
from fielder_backend_utils.multi_batch import MultiBatch



class TestMultiBatch(TestCase):
    def test_multi_batch(self):
        db = FirebaseHelper.getInstance().db

        batch = MultiBatch(db)
        col = db.collection("batch_test")
        for i in range(1200):
            ref = col.document(f"{i}")
            print(
                "value",
                i,
                "number batches",
                batch.number_batches(),
                "number writes",
                batch.number_writes(),
            )
            batch.set(ref, {"data": i}, merge=True)
            assert batch.number_batches() == (i // 500) + 1
            assert batch.number_writes() == i + 1

        print(
            "complete",
            "number batches",
            batch.number_batches(),
            "number writes",
            batch.number_writes(),
        )
        batch.commit()
        print(
            "commited",
            "number batches",
            batch.number_batches(),
            "number writes",
            batch.number_writes(),
        )
        assert batch.number_batches() == 1
        assert batch.number_writes() == 0
        for i in range(1200):
            ref = col.document(f"{i}")
            print(
                "value",
                i,
                "number batches",
                batch.number_batches(),
                "number writes",
                batch.number_writes(),
            )
            batch.set(ref, {"data2": i}, merge=True)
            assert batch.number_batches() == (i // 500) + 1
            assert batch.number_writes() == i + 1


        batch.commit()
        docs = col.get()
        assert len(docs) == 1200
        docs = {d.id: d.to_dict() for d in docs}
        docs_compare = {f"{i}": {"data": i, "data2": i} for i in range(1200)}

        assert(docs == docs_compare)


        for i in range(1200):
            ref = col.document(f"{i}")
            batch.delete(ref)
            assert batch.number_batches() == (i // 500) + 1
            assert batch.number_writes() == i + 1

        batch.commit()

        docs = col.get()
        assert len(docs) == 0
