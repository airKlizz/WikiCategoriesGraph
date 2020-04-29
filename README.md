# WikiCategoriesGraph

The original idea was to use Wikipedia categories to link entities. In another [repo](https://github.com/airKlizz/Wikification) I extract concepts/entities from a list of ranked passages and I would link these entities in order to find what they have in common. I thought Wikipedia categories which link Wikipedia articles could be good to do it. Unfortunately, **it does not work** for at least these reasons:

* there is no a Wikipedia article for each entities,
* Wikipedia categories does not describe the article well (or one category is good and the others are factual like [1919_births](https://en.wikipedia.org/wiki/Category:1919_births)
* too many categories so difficult to link them except for very general categories (example: to link [Nobel peace prize](https://en.wikipedia.org/wiki/Category:Nobel_Peace_Prize) and [BBC 100 Women](https://en.wikipedia.org/wiki/Category:BBC_100_Women) you need to make 3 steps for each in the categories tree to find the category [Awards](https://en.wikipedia.org/wiki/Category:Awards))

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://drive.google.com/open?id=1gp8Z5WkPYHP6e_g641mpkEINQYJmMvoU)
