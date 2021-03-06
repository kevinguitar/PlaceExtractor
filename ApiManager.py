import googlemaps
from googlemaps import places
from googlemaps import distance_matrix
from LocalProperties import API_KEY
from time import sleep


def get_places(conditions):
    gmaps = googlemaps.Client(key=API_KEY)
    __next_page_token = None
    __result = []

    while True:
        page_result = __get_places_by_page(gmaps, conditions, __next_page_token)

        # Get transportation time for multiple destinations
        transport = __get_transport_time(gmaps, conditions.location, page_result['results'])

        # Iterate each place to get detail information
        for i, place in enumerate(page_result['results']):
            detail = __get_places_details(gmaps, place['place_id'])
            # Merge two dict and append to result
            __result.append({**place, **detail, **transport[i]})

        if 'next_page_token' in page_result:
            __next_page_token = page_result['next_page_token']
            continue
        else:
            break

    return __result


def __get_places_by_page(gmaps, conditions, next_page_token):
    results = places.places_nearby(
        client=gmaps,
        location=conditions.location,
        language='zh-TW',
        keyword=conditions.keyword,
        radius=conditions.radius,
        rank_by='distance' if conditions.radius is None else None,
        page_token=next_page_token
    )
    sleep(2)
    return results


def __get_places_details(gmaps, place_id):
    detail = places.place(
        client=gmaps,
        place_id=place_id,
        fields=places.PLACES_DETAIL_FIELDS_CONTACT,
        language='zh-TW'
    )
    return detail['result']


def __get_transport_time(gmaps, origin, destinations):
    destination_locations = list(map(__map_place_to_location, destinations))
    transport = distance_matrix.distance_matrix(
        client=gmaps,
        origins=origin,
        destinations=destination_locations,
        mode='driving',
        language='zh-TW',
    )
    return transport['rows'][0]['elements']


def __map_place_to_location(place):
    return place['geometry']['location']
