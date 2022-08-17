from google.cloud.firestore_v1.batch import WriteBatch
import inspect


class MultiBatch:
    def __init__(self, db):
        self.db = db
        self.batches = [db.batch()]

    def number_batches(self):
        return len(self.batches)

    def number_writes(self):
        return sum(len(b._write_pbs) for b in self.batches)

    def commit(self):
        for batch in self.batches:
            batch.commit()
        self.batches = [self.db.batch()]

    def _get_batch(self):
        if len(self.batches[-1]._write_pbs) == 500:
            self.batches.append(self.db.batch())
        return self.batches[-1]


def _make_wrapped_batch_method(name):
    def func(self, *args, **kwargs):
        batch = self._get_batch()
        return getattr(batch, name)(*args, **kwargs)

    return func


for name, _ in inspect.getmembers(WriteBatch, predicate=inspect.isfunction):
    if name.startswith("_") or name == "commit":
        continue
    setattr(MultiBatch, name, _make_wrapped_batch_method(name))
