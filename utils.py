import math
import numpy as np


def cal_distance(origin_lat, origin_long, dest_lat, dest_long):
    """ It calculates the great-circle distance by Haversine formula.
    Args:
        origin_lat: origin latitude
        origin_long: origin longitude
        dest_lat: destination latitue
        dest_long: destination longitude
    Returns:
        the great-circle distance b/w the two point
    """
    # To check if all are present
    if not all([origin_lat, origin_long, dest_lat, dest_long]):
        return 0
    radius = 3959  # Radius of Earth(miles)
    dlat = math.radians(dest_lat - origin_lat)
    dlon = math.radians(dest_long - origin_long)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(origin_lat)) \
        * math.cos(math.radians(dest_lat)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = radius * c
    return distance


def cal_distance_match(prop_distance, valid_min=2.0, valid_max=10.0):
    """ It calcuates the subtotal match % for distance
    Args:
        prop_distance: (miles), distance calculated by Haversine formula.
        valid_min:(miles) properties below this value will be consider as full match %(inclusive)
        valid_max:(miles) properties below this value will be consider for valid cases (inclusive).
    Returns:
        value b/w (0 and 1), can be considered as distance match %
    """
    if prop_distance <= valid_min:
        return 1
    if valid_min < prop_distance <= valid_max:
        return 1.0 - ((1.0 / (valid_max - valid_min)) * (prop_distance - valid_min))
    return 0


def cal_room_match(property_room, req_min, req_max, valid_uncert=2):
    """ It calculates the subtotal match%  for bedroom/bathroom.
    Args:
        property_room: No. of rooms in a property (Seller side)
        req_min: Minimum No. of rooms required (Buyer side)
        req_max: Maximum No. of rooms required (Buyer side)
        valid_uncert: Uncertainity for +/- room for valid cases
    Returns:
        value b/w (0 and 1), can be considered as bathroom/bedroom match %
    """
    if req_min and req_max:
        if req_min <= property_room <= req_max:
            return 1
        diff_room = (property_room - req_max) if property_room > req_max else req_min - property_room
        return 1.0 - ((1.0 / (valid_uncert + 1)) * diff_room) if (0 < diff_room <= valid_uncert) else 0
    req_room = int(req_min or 0) + int(req_max or 0)
    if (req_room > 1) and (req_room - valid_uncert <= property_room <= req_room + valid_uncert):
        return 1.0 - ((1.0 / (valid_uncert + 1)) * abs(property_room - req_room))
    return 0


def cal_budget_match(property_budget, req_min, req_max, valid_min=10.0, valid_max=25.0):
    """ It calculates the subtotal match % for budget
    Args:
        property_budget: Property price (Seller side)
        req_min: Mininum Budget (Buyer side)
        req_max: Maximum Budget (Buyer side)
        valid_min:(in percentage 0 to 100), when either min or max is given
            +/- valid_min %, will be consider as full match.
        valid_max: (in percentage 0 to 100), +/- valid_max %, will be considered as valid
    Returns:
        value b/w (0 and 1), can be considered as budget match %
    """
    if (req_min and req_max) or (not req_min and not req_max):
        if (req_min <= property_budget <= req_max) or (not req_min and not req_max):
            return 1
        lw = req_min * ((100 - valid_max) / 100) - 0.001  #adding bias
        if lw <= property_budget < req_min:
            return (property_budget - lw) / (req_min - lw)
        hr = req_max * ((100 + valid_max) / 100) + 0.001  #adding bias
        if req_max < property_budget <= hr:
            return 1.0 - ((property_budget - req_max) / (hr - req_max))
        return 0
    req_budget = int(req_min or 0) + int(req_max or 0)
    if req_budget * ((100 - valid_min) / 100) <= property_budget <= req_budget * ((100 + valid_min) / 100):
        return 1
    if req_budget * ((100 - valid_max) / 100) <= property_budget <= req_budget * ((100 + valid_max) / 100):
        diff_per = (abs(property_budget - req_budget) * 100 / req_budget) - valid_min - 0.001  #adding bias
        return 1.0 - (diff_per / (valid_max - valid_min))
    return 0


def cal_total(property_, requirement, weightage):
    """ It calculates the total match percentages for each bedroom, bathroom, budget, distance and
        sum up all according to their weighage.
    Args:
        property_(dict): property data
        requirement(dict): Requirement data
        weightage(dict): defined weightages for each.
    """
    distance = cal_distance(float(property_["latitude"]), float(property_["longitude"]), float(requirement["latitude"]),
                                     float(requirement["longitude"]))
    subtotal_distance = cal_distance_match(distance)
    subtotal_bedroom = cal_room_match(float(property_["n_bedrooms"]), float(requirement["min_bedrooms"]),
                                      float(requirement["max_bedrooms"]))
    subtotal_bathroom = cal_room_match(float(property_["n_bathrooms"]), float(requirement["min_bathrooms"]),
                                       float(requirement["max_bathrooms"]))
    subtotal_budget = cal_budget_match(float(property_["price"]), float(requirement["min_budget"]),
                                       float(requirement["max_budget"]))
    
    ret_dict = {"property_id": property_["id"], "requirement_id": requirement["id"],
                "distance": round(subtotal_distance * weightage["distance"], 2),
                "bedroom": round(subtotal_bedroom * weightage["bedroom"], 2),
                "bathroom": round(subtotal_bathroom * weightage["bathroom"], 2),
                "budget": round(subtotal_budget * weightage["budget"], 2),
                }
    ret_dict["total"] = round(sum([ret_dict["distance"], ret_dict["bedroom"], ret_dict["bathroom"], ret_dict["budget"]]), 2)
    return ret_dict
