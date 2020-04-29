import requests
import networkx as nx
import numpy as np
import json
from tqdm import tqdm

cookies = {"session":"2b1bc02f-cb61-4e6c-9f22-e80cb74e3e3b"}

with open('WikiSQL/sql_requests/categories.sql', 'r') as f:
    categories_template = f.read()

with open('WikiSQL/sql_requests/family.sql', 'r') as f:
    family_template = f.read()

with open('WikiSQL/sql_requests/category_pages.sql', 'r') as f:
    category_pages_template = f.read()

def flatten(A):
    rt = []
    for i in A:
        if isinstance(i,list): rt.extend(flatten(i))
        else: rt.append(i)
    return rt

def do_sql_requests(sql_requests, cookies):
	request = '\n'.join(sql_requests)
	num_requests = len(sql_requests)
	with requests.Session() as s:
		post_url = 'https://quarry.wmflabs.org/api/query/run'
		data = {"text": request, "query_id":"44159"}
		r = s.post(post_url, data=data, cookies=cookies)
		qrun_id = json.loads(r.content)['qrun_id']
		status_url = "https://quarry.wmflabs.org/run/{}/status".format(qrun_id)
		while True:
			r = s.get(status_url, cookies=cookies)
			if r.json()['status'] == 'complete':
				break

		output_url_template = 'https://quarry.wmflabs.org/run/{}/output/{}/json'
		output = []
		for i in range(num_requests):
			output_url = output_url_template.format(qrun_id, i)
			r = s.get(output_url, cookies=cookies)
			rows = r.json()['rows']
			output.append(rows)
		return output

def list_to_string(list):
    string = ''
    for elem in list:
        string += '\''+ str(elem).replace('\'', '\\\'') +'\'' + ', '
    string = string[:-2]
    return string

def get_categories_one_batch(article_ids):
    sql_requests = []
    for article_id in article_ids:
        sql_requests.append(categories_template.format(article_id))
    output = do_sql_requests(sql_requests, cookies)
    return {article_id: flatten(output[i]) for i, article_id in enumerate(article_ids)}

def get_categories(article_ids, batch_size=10):
    categories = {}
    for i in tqdm(range(0, len(article_ids), batch_size), desc="Find categories in progress..."): 
        batch_article_ids = article_ids[i : min(i+batch_size, len(article_ids))]
        categories.update(get_categories_one_batch(batch_article_ids))
    return categories  

def get_categories_from_id(article_id):
    sql_requests = [
        categories_template.format(article_id)
    ]
    output = do_sql_requests(sql_requests, cookies)
    return flatten(output[0])

def get_num_pages_one_batch(titles):
    sql_requests = [
        category_pages_template.format(list_to_string(titles))
    ]
    output = do_sql_requests(sql_requests, cookies)
    return {row[0]: row[1] for row in output[0]}

def get_num_pages(titles, batch_size=10):
    categories_num_pages = {}
    for i in tqdm(range(0, len(titles), batch_size), desc="Find number of pages per category in progress..."): 
        batch_titles = titles[i : min(i+batch_size, len(titles))]
        categories_num_pages.update(get_num_pages_one_batch(batch_titles))
    return categories_num_pages   

def get_family(category):
    sql_requests = [
        family_template.format(category)
    ]

    output = do_sql_requests(sql_requests, cookies)
    return output[0]

def get_families(categories):
    output  = []
    for category in tqdm(categories):
        output += get_family(category)
    return output

def get_kinship_subcats(families):
    kinship = [] # list of set (parent_cat, cat)
    subcats = {} # dict {cat: number of subcats}
    for row in families:
        for i in range(0, len(row), 2):
            if i+1 >= len(row): 
                subcats[row[i]] = 1
                continue
            subcats[row[i]] = int(row[i+1])
            kinship.append((row[i], row[i+2]))
    all_categories = list(subcats.keys())
    return all_categories, kinship, subcats

def create_P(all_categories, families, factor, weight_edge):
    G = nx.DiGraph()
    for cat in all_categories:
      G.add_node(cat)
    for row in families:
      for i in range(0, len(row)-1, 2):
        parent = row[i]
        child = row[i+2]
        if weight_edge:
            weight = factor/max(np.log(row[i+1]), 1)
        else:
            weight = factor
        G.add_edge(child, parent, weight=weight)

    P = nx.to_numpy_matrix(G)
    return np.array(P), G

def create_pi(categories_score, all_categories):
    pi = np.zeros(len(all_categories))
    for i, category in enumerate(all_categories):
        if category in categories_score.keys():
            pi[i] = categories_score[category]
    return pi

def get_pi_P(categories_score, top_n=None, factor=0.8, weight_edge=True):
    categories = sorted(categories_score, key=categories_score.get, reverse=True)[:top_n]
    families = get_families(categories)
    all_categories, kinship, subcats = get_kinship_subcats(families)
    pi = create_pi(categories_score, all_categories)
    P, _ = create_P(all_categories, families, factor, weight_edge)
    return pi, P, all_categories