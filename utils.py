import json
import requests
from tqdm import tqdm
import signal
from contextlib import contextmanager

from WikiSQL.utils import get_categories_from_id, get_num_pages, get_pi_P

import numpy as np

example = 'data/Livestream during quarantine.json'

@contextmanager
def timeout(time):
    # Register a function to raise a TimeoutError on the signal.
    signal.signal(signal.SIGALRM, raise_timeout)
    # Schedule the signal to be sent after ``time``.
    signal.alarm(time)
    try:
        yield
    except TimeoutError:
        pass
    finally:
        # Unregister the signal so it won't be triggered
        # if the timeout is not reached.
        signal.signal(signal.SIGALRM, signal.SIG_IGN)

def raise_timeout(signum, frame):
    raise TimeoutError

def load_entities_scores(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def get_article(entity):
    url_template = "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={}&utf8=&format=json&srlimit=1"
    entity = entity.replace(' ', '_')
    url = url_template.format(entity)
    try:
        with timeout(5):
            results = requests.get(url).json()
    except:
        print('{}: article not got'.format(entity))
        return None
    results = results['query']['search']
    if len(results) == 0: return None
    return results[0]['pageid']

def get_categories_from_entities(entities_scores, idf=True):

    wiki_ids_entities = {}
    for entity in tqdm(entities_scores.keys(), desc='Find ids in progress...'):
        wiki_ids_entities[get_article(entity)] = entity

    ids_categories = {}
    for id in tqdm(list(wiki_ids_entities.keys()), desc='Find categories in progress...'):
        if id in ids_categories.keys(): continue
        try:
            with timeout(5):
                ids_categories[id] = get_categories_from_id(id)
        except:
            print('{}: categories not got'.format(wiki_ids_entities[id]))
            pass

    entities_categories = {wiki_ids_entities[k]: v for k, v in ids_categories.items()}

    categories_entities = {}
    categories_scores = {}
    for entity, categories in entities_categories.items():
        for category in categories:

            # remove parasit categories
            if 'Wiki' in category or 'isambiguation_pages' in category or 'topic_articles' in category or 'Living_people' in category: continue

            if category in categories_entities.keys():
                categories_entities[category].append(entity)
                categories_scores[category] += entities_scores[entity]
            else:
                categories_entities[category] = [entity]
                categories_scores[category] = entities_scores[entity]

    if idf:
        categories_num_pages = get_num_pages(list(categories_scores.keys()), 50)
        categories_scores = {k: v/max(np.log(categories_num_pages[k]), 1) if k in categories_num_pages.keys() else v for k, v in categories_scores.items()}

    return categories_scores, entities_categories

def run_graph(entities_scores, categories_scores, entities_categories, top_n=None, factor=0.8, weight_edge=True, depth=3):
    pi, P, all_categories = get_pi_P(categories_scores, top_n=top_n, factor=factor, weight_edge=weight_edge)
    pi_1 = pi + np.dot(pi, P)
    pi_2 = pi_1 + np.dot(pi_1, P)
    pi_3 = pi_2 + np.dot(pi_2, P)

    best_parents_scores = {}
    best_parents_titles = {}
    for title in tqdm(sorted(entities_scores, key=entities_scores.get, reverse=True), desc='Find best parent in progress...'):

        if title not in entities_categories.keys():
            print('{} not in entities categories'.format(title))
            continue

        score = entities_scores[title]
        best_category = get_best_parent(title, entities_categories, categories_scores, P, pi_3, all_categories, depth)

        if best_category == None or 'isambiguation_pages' in best_category or 'topic_articles' in best_category or 'Living_people' in best_category or 'Main_topic_classifications' in best_category: continue

        if best_category in best_parents_scores.keys():
            best_parents_scores[best_category] += score
            best_parents_titles[best_category].append(title)
        else:
            best_parents_scores[best_category] = score
            best_parents_titles[best_category] = [title]

    return best_parents_scores, best_parents_titles

def get_parents(category, P, all_categories):
    row = P[all_categories.index(category)]
    parents = [all_categories[i] for i in range(len(row)) if row[i] > 0.0]
    return parents

def get_best_parent_from_category(category, P, pi, all_categories, step, step_max):
    if step == step_max:
        return category
    else:
        parents = get_parents(category, P, all_categories)
        best_parent = category
        best_score = pi[all_categories.index(category)]
        for parent in parents:
            candidate = get_best_parent_from_category(parent, P, pi, all_categories, step+1, step_max)
            candidate_score = pi[all_categories.index(candidate)]
            if candidate_score > best_score:
                best_score = candidate_score
                best_parent = candidate
        return best_parent

def get_best_parent(title, titles_categories, categories_scores, P, pi, all_categories, step_max):
    categories = titles_categories[title]
    best_parent = None
    best_score = 0.0
    for category in categories:
        if category in all_categories:
            candidate = get_best_parent_from_category(category, P, pi, all_categories, 0, step_max)
            candidate_score = pi[all_categories.index(candidate)]
        else:
            candidate = category
            if candidate in categories_scores.keys():
                candidate_score = categories_scores[candidate]
            else: 
                candidate_score = 0.01
        if candidate_score > best_score:
            best_score = candidate_score
            best_parent = candidate
    return best_parent

def extract_best_parents_scores_and_best_parents_titles(entities_scores, idf_for_categories=True, top_n=100, factor=0.8, weight_edge=True):
    categories_scores, entities_categories = get_categories_from_entities(entities_scores, idf=idf_for_categories)
    return run_graph(entities_scores, categories_scores, entities_categories, top_n=top_n, factor=factor, weight_edge=weight_edge)