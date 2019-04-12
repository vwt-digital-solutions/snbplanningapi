from flask import jsonify


def cars_get():  # noqa: E501
    """Get car locations

    Get a list of all car geolocations # noqa: E501


    :rtype: Cars
    """
    exampleresult = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        5.3,
                        52.6
                    ]
                },
                "properties": {
                    "license_plate": "AA-BB-11"
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        5.4,
                        52.5
                    ]
                },
                "properties": {}
            }
        ]
    }

    return jsonify(exampleresult)
