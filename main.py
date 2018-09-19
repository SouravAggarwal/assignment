import json
import time
from utils import cal_total


def fetch_valid_properties():
    """ It defines all tweaking parameters like (weightage, validthreshold)
        and calculates the match % for each buyer with all properties.

    Returns:
        It returns a dict, where key is requirement id and value is a list of matching properties with their match percentages.
        {"requirement id": List of matching properties,  "requirement id": list of matching properties }
    """
    # define Weightage in %
    weightage = {}
    weightage["distance"] = 30
    weightage["budget"] = 30
    weightage["bathroom"] = 20
    weightage["bedroom"] = 20

    # final matches above 40% will be considered as useful
    valid_threshold = 40

    # Import data
    with open('dummydata.json') as f:
        data = json.load(f)

    resp = {}
    for requirement in data["requirements"]:
        valid_properties = []
        for property_ in data["properties"]:
            final_data = cal_total(property_, requirement, weightage)
            if final_data["total"] >= valid_threshold:
                valid_properties.append(final_data)       
        resp[requirement["id"]] = valid_properties
    return resp


if __name__ == "__main__":
    response = fetch_valid_properties()
    print(json.dumps(response))
