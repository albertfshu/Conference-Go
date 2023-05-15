from django.http import JsonResponse
from common.json import ModelEncoder
from django.views.decorators.http import require_http_methods
import json
from .models import ConferenceVO, Attendee


class ConferenceVODetailEncoder(ModelEncoder):
    model = ConferenceVO
    properties = ["name", "import_href"]


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
    encoders = {
        "conference": ConferenceVODetailEncoder(),
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
def api_list_attendees(request, conference_vo_id=None):
    if request.method == "GET":
        attendees = Attendee.objects.filter(conference=conference_vo_id)
        # attendees = Attendee.objects.filter(id=conference_id)
        return JsonResponse(
            {"attendees": attendees}, encoder=AttendeeListEncoder, safe=False
        )
    else:
        content = json.loads(request.body)
    try:
        conference_href = f"/api/conferences/{conference_vo_id}/"
        conference = ConferenceVO.objects.get(import_href=conference_href)
        content["conference"] = conference
    except ConferenceVO.DoesNotExist:
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
