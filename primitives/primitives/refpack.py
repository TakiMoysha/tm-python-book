def weakref_value_dict():
    from weakref import WeakValueDictionary

    class ApplicationObject: ...

    async def should_removed_prepared_object_in_weakref_dict():
        """weakref: Example where a prepared object is removed from a WeakValueDictionary"""
