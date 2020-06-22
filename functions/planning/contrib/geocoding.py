def geocode_address(gmaps, entity):
    """This function tries to geocode an entity from it's fields.
    It returns an updated entity with a geometry field containing a Point and coordinates."""
    if 'zip' in entity and entity['zip'] != '':
        postcode = ''.join([ch for ch in entity['zip'] if ch != ' '])
        location = gmaps.geocode(postcode)
    elif 'city' in entity and entity['city'] != '':
        address = entity['city'] + ',Nederlands'
        if 'street' in entity and entity['street'] != '':
            address = entity['street'] + ',' + address
        location = gmaps.geocode(address)

    entity.update({'geometry': {
        "type": "Point",
        "coordinates": [
            location[0]['geometry']['location']['lng'],
            location[0]['geometry']['location']['lat']
        ]
    }})
    return entity
