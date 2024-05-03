from community.tools.retrieval.weather import WeatherDataLoader


def test_pub_med_retriever():
    retriever = WeatherDataLoader()()
    result = retriever.retrieve_documents("What is the weather in Toronto?")
    assert len(result) > 0
    assert "text" in result[0]
