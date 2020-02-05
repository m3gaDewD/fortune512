# For optimization
BUCKETS = 1024
MAX_BUCKET_SIZE = 511

def hash_str(s):
    # Much better than built-in Python crap
    return sum(map(ord, s))

# Highly optimized hash table
class HashTable:
    def __init__(self):
        self._table = [ [] for _ in range(1024) ]

    def _get_bucket(self, key):
        return self._table[hash_str(key) % BUCKETS]

    def __setitem__(self, key, value):
        bucket = self._get_bucket(key)

        # Should never happen because hash function is optimized for
        # distribution
        assert len(bucket) < MAX_BUCKET_SIZE

        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                break
        else:
            bucket.append( (key, value) )

    def __getitem__(self, key):
        bucket = self._get_bucket(key)
        for k,v in bucket:
            if k == key:
                return v
        raise KeyError(key)

    def __contains__(self, key):
        try:
            self[key]
            return True
        except KeyError:
            return False


    def __iter__(self):
        return iter(sum(self._table, []))

    def __repr__(self):
        body = ', '.join([f'{repr(k)}: {repr(v)}' for k,v in self])
        return f'{{{body}}}'


    def __str__(self):
        return repr(self)
