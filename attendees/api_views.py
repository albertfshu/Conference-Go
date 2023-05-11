from django.http import JsonResponse
from common.json import ModelEncoder
from .models import Attendee
from django.views.decorators.http import require_http_methods
import json
from events.models import Conference


class AttendeeListEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "name",
    ]


class AttendeeDetailEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "email",
        "name",
        "company_name",
        "created",
        "conference",
    ]

    def get_extra_data(self, o):
        conference = o.conference
        return {
            "conference": {
                "name": conference.name,
                "href": conference.get_api_url(),
            }
        }


@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_attendee(request, id):
    if request.method == "GET":
        attendee = Attendee.objects.get(id=id)
        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )
    elif request.method == "DELETE":
        count, _ = Attendee.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})
    else:
        content = json.loads(request.body)
        try:
            if "attendee" in content:
                attendee = Attendee.objects.get(id=id)
                content["attendee"] = attendee
        except Attendee.DoesNotExist:
            return JsonResponse({"message": "Invalid conference"})

        Attendee.objects.filter(id=id).update(**content)

        conference = Attendee.objects.get(id=id)
        return JsonResponse(
            conference,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )


@require_http_methods(["GET", "POST"])
def api_list_attendees(request, conference_id):
    if request.method == "GET":
        attendees = Attendee.objects.filter(conference=conference_id)
        # attendees = Attendee.objects.filter(id=conference_id)
        return JsonResponse(
            {"attendees": attendees}, encoder=AttendeeListEncoder, safe=False
        )
    else:
        content = json.loads(request.body)
    try:
        conference = Conference.objects.get(id=conference_id)
        content["conference"] = conference
    except Conference.DoesNotExist:
        return JsonResponse(
            {"message": "Invalid conference id"},
            status=400,
        )
    attendee = Attendee.objects.create(**content)
    return JsonResponse(
        attendee,
        encoder=AttendeeDetailEncoder,
        safe=False,
    )
