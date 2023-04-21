import json
import requests
from .pywikigraph import WikiGraph
from .graph import categories

wg = WikiGraph()


def get_shortest_path(source, dest):
    paths = wg.get_shortest_paths_info(source, dest)
    return paths


def get_nearest_wiki_links(keyword):
    """
    It takes a keyword and returns a list of the top 10 Wikipedia links that are related to that keyword

    :param keyword: The keyword you want to search for
    :return: A list of the top 10 wikipedia links related to the keyword
    """
    URL = "https://en.wikipedia.org/w/api.php"
    PARAMS = {"action": "opensearch", "search": keyword}
    r = requests.get(url=URL, params=PARAMS)
    data = r.json()[1]
    return data


def get_shortest_path_details(source: str, dest: str) -> None:
    data = get_shortest_path(source, dest)
    # print(data)
    return [dest, data[0], data[1]]


def get_categories_sp(source: str):
    data = []
    for i in categories:
        data.append(get_shortest_path_details(source, i))
    min = 5
    for i in data:
        if i[1] < min:
            min = i[1]
    data_selected = []
    for i in data:
        if i[1] == min:
            data_selected.append(i)
    data_sorted = sorted(data_selected, key=lambda i: i[2], reverse=True)
    with open(f"data_{source}.json", "w") as f:
        json.dump(data_sorted, f)
    print("Data written.")
    return data_sorted


def wiki_test():
    get_categories_sp("Elon Musk")


if __name__ == "__main__":
    pass
