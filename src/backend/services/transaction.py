def validate_transaction(func):
    def wrapper(*args, **kwargs):
        if "db" in kwargs:
            db = kwargs["db"]
        else:
            db = args[0]

        try:
            return func(*args, **kwargs)
        except Exception as e:
            db.rollback()
            raise e

    return wrapper
