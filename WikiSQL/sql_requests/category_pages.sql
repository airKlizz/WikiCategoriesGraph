select cat_title, cat_pages-cat_subcats
from category
where cat_title in ({});