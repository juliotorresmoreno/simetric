
from django.shortcuts import render
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.db import connection
import json


def operation_eq(operator: str, key: str, value: str):
    if operator == 'eq':
        return " AND %s = '%s'" % (key, value)
    return ''


def operation_neq(operator: str, key: str, value: str):
    if operator == 'eq':
        return " AND %s <> '%s'" % (key, value)
    return ''


def operation_like(operator: str, key: str, value: str):
    if operator == 'like':
        return " AND " + key + " like '%" + value + "%'"
    return ''


def operation_gt(operator: str, key: str, value: str):
    if operator == 'gt':
        return " AND %s > '%s'" % (key, value)
    return ''


def operation_lt(operator: str, key: str, value: str):
    if operator == 'lt':
        return " AND " + key + " < '%" + value + "%'"
    return ''


def operation_gte(operator: str, key: str, value: str):
    if operator == 'gte':
        return " AND %s >= '%s'" % (key, value)
    return ''


def operation_lte(operator: str, key: str, value: str):
    if operator == 'lte':
        return " AND %s <= '%s'" % (key, value)
    return ''


operations = [
    operation_eq,
    operation_neq,
    operation_like,
    operation_gt,
    operation_lt,
    operation_gte,
    operation_lte
]


def is_secure(value: str):
    # TODO: validacion de inyeccion SQL
    if (';' in value):
        return False
    return True


def construct_where(data: dict):
    condition = '1=1'
    keys = [x for x in data.keys()
            if not x in ['limit', 'sort']
            and data.get(x, None) != None
            ]
    for key in keys:
        value = data.get(key, None)
        if not is_secure(value):
            continue
        tmp = value.split(':')
        if len(tmp) == 1:
            condition = condition + " AND %s = '%s'" % (key, value)
        else:
            operator = tmp[0]
            value = tmp[1]
            for op in operations:
                el = op(operator, key, value)
                condition = condition + el
                if el != '':
                    break
    return condition


def construct_sort(value: str):
    if value == '':
        return ''
    tmp = value.split(',')
    results = []
    for el in tmp:
        s = el.split(':')
        field = s[0]
        if len(s) == 2:
            sort = s[1]
        else:
            sort = 'desc'
        results.append(field + ' ' + sort)
    return 'ORDER BY ' + ', '.join(results)


def get_index(request: WSGIRequest, table: str):
    result = []
    limit = request.GET.get('limit', '0,10')
    condition = construct_where(request.GET)
    sort = construct_sort(request.GET.get('sort', '0,10'))

    with connection.cursor() as cursor:
        sql = """
            SELECT * 
              FROM %s
             WHERE %s
             %s
             LIMIT %s;
            """ % (table, condition, sort, limit)
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        for row in cursor:
            result.append(row)

    data = json.dumps({
        "columns": columns,
        "data": result,
        "limit": limit
    })

    response = HttpResponse(data)
    response['Content-Type'] = 'application/json'
    return response
