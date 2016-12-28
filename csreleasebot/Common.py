import yaml
import re


def makeCommonResponse(speech):
    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "csreleasebot"
    }


def getParameter(req, contextName, parameterName):
    result = req.get("result")
    parameters = result.get('parameters')
    contexts = result.get('contexts')
    contextParameters = None
    for context in contexts:
        if context.get('name') == contextName:
            contextParameters = context.get('parameters')

    parameter = parameters.get(parameterName)
    if parameter is None:
        if contextParameters is not None:
            parameter = contextParameters.get(parameterName)
    return parameter


def extractParametersFromText(text):
    return re.findall(r"\{([A-Za-z0-9_\\.]+)\}", text)


def fillParameters(valuesToFill, text):
    parameters = extractParametersFromText(text)
    for parameter in parameters:
        value = __handleChildParameters(valuesToFill, parameter.split('.'), None)
        if callable(value):
            value = value(valuesToFill)
        if value is not None:
            text = text.replace('{' + parameter + '}', value)
    return text


def __handleChildParameters(valuesToFill, parameterParts, child):
    if len(parameterParts) == 0:
        return child
    else:
        part = parameterParts.pop(0)
        if child is None:
            child = valuesToFill.get(part)
        else:
            child = child.__dict__.get(part)
        return __handleChildParameters(valuesToFill, parameterParts, child)


def getMessageFromFile(fileName, modelName, parameters):
    allModels = yaml.load(open(fileName, 'r'))
    model = allModels.get(modelName)
    return __handleItems(model, parameters)


def __handleItems(model, parameters):
    matchLevel = [None]*len(model)
    for i, item in enumerate(model):
        matchLevel[i] = 0
        for parameterName, parameterValue in parameters.iteritems():
            if parameterName in item:
                matchLevel[i] -= 1000
                itemValue = item.get(parameterName)
                if isinstance(itemValue, list):
                    if parameterValue in itemValue:
                        matchLevel[i] += 1000
                elif parameterValue == itemValue:
                    matchLevel[i] += 1000
    match = model[matchLevel.index(max(matchLevel))] #TODO: if matchLevel=0 what to do, means default or sth
    if 'sub' in match:
        return __handleItems(match.get('sub'), parameters)
    else:
        return match.get('msg')
