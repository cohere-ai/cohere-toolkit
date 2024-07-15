class AsyncGeneratorContextManager:
    def __init__(self, agen):
        self._agen = agen

    async def __aenter__(self):
        return self._agen

    async def __aclose__(self, *args):
        await self._agen.aclose()

    async def __aexit__(self, exc_type, exc, tb):
        pass
