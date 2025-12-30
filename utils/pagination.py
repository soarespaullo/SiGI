from flask import request

def paginate_query(query, per_page=10):
    """
    Helper para aplicar paginação em qualquer query SQLAlchemy.
    - query: objeto query (ex: User.query)
    - per_page: número de registros por página
    """
    page = request.args.get("page", 1, type=int)
    return query.paginate(page=page, per_page=per_page)
