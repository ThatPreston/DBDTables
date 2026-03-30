# Basic serializer to convert python data into lua. Only supports basic types required by cosmetics

def serialize(data, compact, minIndentToCompact, indentLevel):
    compact = compact or indentLevel >= minIndentToCompact
    if isinstance(data, str):
        data = data.replace('"', '\\"').replace('\n', '\\n').replace('\\„', '„').replace('\\”', '”')
        return f"\"{data}\""
    elif isinstance(data, bool):
        return str(data).lower()
    elif isinstance(data, (int, float)):
        return str(data)
    elif isinstance(data, list):
        parts = ["{"]
        last = len(data) - 1
        if compact:
            for i, item in enumerate(data):
                parts.append(serialize(item, compact, minIndentToCompact, indentLevel))
                if i < last:
                    parts.append(", ")
        else:
            parts.append("\n")
            indentLevel += 1
            for i, item in enumerate(data):
                parts.append("\t" * indentLevel)
                parts.append(serialize(item, compact, minIndentToCompact, indentLevel))
                if i < last:
                    parts.append(",")
                parts.append("\n")
            indentLevel -= 1
            parts.append("\t" * indentLevel)
        parts.append("}")
        return "".join(parts)
    elif isinstance(data, dict):
        parts = ["{"]
        last = len(data) - 1
        if compact:
            i = 0
            for key, value in data.items():
                parts.append(key + " = " + serialize(value, compact, minIndentToCompact, indentLevel))
                if i < last:
                    parts.append(", ")
                i += 1
        else:
            parts.append("\n")
            indentLevel += 1
            i = 0
            for key, value in data.items():
                parts.append("\t" * indentLevel)
                parts.append(key + " = " + serialize(value, compact, minIndentToCompact, indentLevel))
                if i < last:
                    parts.append(",")
                parts.append("\n")
                i += 1
            indentLevel -= 1
            parts.append("\t" * indentLevel)
        parts.append("}")
        return "".join(parts)
    elif data is None:
        return "nil"
    print("Tried to serialize an unsupported data type!", data)
    return "nil"