select grand_grand_parent.grand_grand_parent_title, category.cat_subcats as grand_grand_parent_subcats, grand_grand_parent.grand_parent_title, grand_grand_parent.grand_parent_subcats, grand_grand_parent.parent_title, grand_grand_parent.parent_subcats, grand_grand_parent.child_title
from category
inner join (select cl1.cl_to as grand_grand_parent_title, grand_parent.grand_parent_title, grand_parent.grand_parent_subcats, grand_parent.parent_title, grand_parent.parent_subcats, grand_parent.child_title
            from categorylinks as cl1 
            inner join (select grand_parent.grand_parent_title, page.page_id as grand_parent_id, grand_parent.grand_parent_subcats, grand_parent.parent_title, grand_parent.parent_subcats, grand_parent.child_title
                        from page
                        inner join (select category.cat_title as grand_parent_title, category.cat_subcats as grand_parent_subcats, grand_parent.parent_title, grand_parent.parent_subcats, grand_parent.child_title
                                    from category
                                    inner join (select cl1.cl_to as grand_parent_title, parent.cat_title as parent_title, parent.page_id as parent_id, parent.cat_subcats as parent_subcats, parent.child_title
                                                from categorylinks as cl1 
                                                inner join (select parent.cat_title, page.page_id, parent.cat_subcats, parent.child_title
                                                            from page
                                                            inner join (select category.cat_title, category.cat_subcats, parent.child_title
                                                                        from category
                                                                        inner join (select cl1.cl_to, p.page_title as child_title
                                                                                    from categorylinks as cl1
                                                                                    inner join (select page_id, page_title
                                                                                                from page 
                                                                                                where page_title = "{}"
                                                                                                and page_namespace = 14 limit 1) as p
                                                                                    on cl1.cl_from = p.page_id
                                                                                    where not "Hidden_categories" in (select cl2.cl_to 
                                                                                                                      from categorylinks as cl2
                                                                                                                      where cl_from = (select page_id 
                                                                                                                                       from page 
                                                                                                                                       where page_title = cl1.cl_to
                                                                                                                                       and page_namespace = 14 
                                                                                                                                       limit 1)
                                                                                                                     )
                                                                                   ) as parent
                                                                        on parent.cl_to = category.cat_title
                                                                       ) as parent
                                                            on parent.cat_title = page.page_title
                                                            and page.page_namespace = 14 
                                                           ) as parent
                                                           on cl1.cl_from = parent.page_id
                                                where not "Hidden_categories" in (select cl2.cl_to 
                                                                                from categorylinks as cl2
                                                                                where cl_from = (select page_id 
                                                                                                 from page 
                                                                                                 where page_title = cl1.cl_to
                                                                                                 and page_namespace = 14 
                                                                                                 limit 1)
                                                                               )

                                                ) as grand_parent
                                                on grand_parent.grand_parent_title = category.cat_title
                                    ) as grand_parent
                                    on grand_parent.grand_parent_title = page.page_title
                                    and page.page_namespace = 14
                        ) as grand_parent
                        on cl1.cl_from = grand_parent.grand_parent_id
            where not "Hidden_categories" in (select cl2.cl_to 
                                              from categorylinks as cl2
                                              where cl_from = (select page_id 
                                                               from page 
                                                               where page_title = cl1.cl_to
                                                               and page_namespace = 14 
                                                               limit 1)
                                             )
            ) as grand_grand_parent
            on grand_grand_parent.grand_parent_title = category.cat_title
