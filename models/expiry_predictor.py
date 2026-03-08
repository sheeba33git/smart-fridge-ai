def predict_expiry(vegetable,freshness):

    if freshness == "Fresh":
        return 5

    if freshness == "Medium":
        return 2

    if freshness == "Spoiled":
        return 0

    return 0