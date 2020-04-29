select cl1.cl_to 
from categorylinks as cl1 
where cl_from = {}
and not "Hidden_categories" in (select cl2.cl_to 
                                from categorylinks as cl2
                                where cl_from = (select page_id 
                                                 from page 
                                                 where page_title = cl1.cl_to
                                                 and page_namespace = 14 
                                                 limit 1)
                               )
;