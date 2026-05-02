from django import template


register = template.Library()


@register.inclusion_tag("includes/pagination.html", takes_context=True)
def render_pagination(context):
    page_obj = context.get("page_obj")
    request = context.get("request")
    if not page_obj:
        return {"page_obj": None, "page_links": []}

    def page_url(number):
        query = request.GET.copy() if request else None
        if query is not None:
            query["page"] = number
            return f"?{query.urlencode()}"
        return f"?page={number}"

    page_links = []
    for page_number in page_obj.paginator.get_elided_page_range(
        page_obj.number,
        on_each_side=2,
        on_ends=1,
    ):
        if page_number == page_obj.paginator.ELLIPSIS:
            page_links.append({"label": page_number, "is_ellipsis": True})
            continue

        page_links.append(
            {
                "number": page_number,
                "label": page_number,
                "url": page_url(page_number),
                "is_current": page_number == page_obj.number,
                "is_ellipsis": False,
            }
        )

    return {
        "page_obj": page_obj,
        "page_links": page_links,
        "previous_url": page_url(page_obj.previous_page_number())
        if page_obj.has_previous()
        else "",
        "next_url": page_url(page_obj.next_page_number()) if page_obj.has_next() else "",
    }
