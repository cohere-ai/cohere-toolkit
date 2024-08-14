def validate_transaction(func):
    def wrapper(*args, **kwargs):
        db = kwargs["db"] if "db" in kwargs else args[0]
        try:
            return func(*args, **kwargs)
        except Exception as e:
            db.rollback()
            raise e

    return wrapper
