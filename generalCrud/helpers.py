import json

def GetBody(request):
    unicode=request.body.decode('utf-8')
    return json.loads(unicode)