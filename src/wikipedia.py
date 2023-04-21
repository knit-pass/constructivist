import json
import requests
import numpy as np
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


def compare(item):
    return (item[1], -item[2])


def get_semantic_percentage(domains):
    domain_counts = {}
    total_score = 0
    for domain in domains:
        domain_counts[domain[0]] = (7000 * (1 / domain[1])) + (25 * domain[2])
        total_score += domain_counts[domain[0]]
    domain_percentages = {}
    for domain in domain_counts:
        percentage = (domain_counts[domain] / total_score) * 100
        domain_percentages[domain] = round(percentage, 2)
    return domain_percentages


def get_categories_sp(source: str):
    data = []
    for i in categories:
        data.append(get_shortest_path_details(source, i))
    min = 5
    for i in data:
        if i[1] < min:
            min = i[1]
    data_selected_primary = []
    data_selected_secondary = []
    for i in data:
        if i[1] == min:
            data_selected_primary.append(i)
        elif i[1] == min + 1 and i[2] > 2:
            data_selected_secondary.append(i)
    data_selected_secondary = sorted(data_selected_secondary, key=lambda s: s[2])
    data_selected = data_selected_primary
    data_selected.extend(data_selected_secondary)
    data_sorted = sorted(data_selected, key=compare)
    final_data = get_semantic_percentage(data_sorted)
    with open(f"data_{source}.json", "w") as f:
        json.dump(final_data, f)
    print("Data written.")
    return final_data


def wiki_test():
    get_categories_sp("Amazon rainforest")
    get_categories_sp("Hinduism")
    get_categories_sp("Algorithm")
    get_categories_sp("Twitter")
    get_categories_sp("Narendra Modi")
    get_categories_sp("Marcus Aurelius")


if __name__ == "__main__":
    pass
